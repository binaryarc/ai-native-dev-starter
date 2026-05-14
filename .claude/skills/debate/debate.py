#!/usr/bin/env python3
"""Claude(claude -p)와 Codex(codex exec)가 헤드리스 CLI로 회의하며 결론을 도출하는 오케스트레이터."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


# ── 에이전트 페르소나 ──────────────────────────────────────────────────────────

CLAUDE_SYSTEM = """당신은 창의적이고 비판적인 사고를 가진 전략가입니다.
Codex(데이터 중심 분석가)와 안건에 대해 토론하며 최선의 결론을 도출합니다.
- 상대 의견의 약점을 짚되, 근거 없는 반박은 하지 않습니다.
- 합의 가능한 부분은 인정하고 수렴합니다.
- 답변은 300자 이내로 간결하게 작성합니다.
- 마지막 라운드에서는 [최종 입장]을 한 문단으로 명확히 정리합니다.
- 파일 읽기, bash 실행 등 도구는 사용하지 마세요. 주어진 내용만 분석합니다."""

CODEX_SYSTEM = """당신은 실용적이고 데이터 중심적인 분석가입니다.
Claude(전략가)와 안건에 대해 토론하며 최선의 결론을 도출합니다.
- 구체적 근거와 실현 가능성을 중심으로 논증합니다.
- 감정적 주장보다 논리적 반론을 우선합니다.
- 답변은 300자 이내로 간결하게 작성합니다.
- 마지막 라운드에서는 [최종 입장]을 한 문단으로 명확히 정리합니다.
- 파일 읽기, bash 실행 등 도구는 사용하지 말고 주어진 내용만 분석합니다."""

MODERATOR_SYSTEM = "당신은 중립적인 토론 사회자입니다. 토론 내용을 요약하고 결론을 도출합니다."

MODERATOR_PROMPT = """위 토론 내용을 바탕으로:
1. Claude와 Codex의 핵심 주장 각 1줄 요약
2. 합의된 결론 (또는 합의 실패 시 핵심 쟁점)
3. 실행 권고안 1가지

300자 이내로 작성하세요."""


# ── Claude 헬퍼 ───────────────────────────────────────────────────────────────

def call_claude(
    message: str,
    *,
    session_id: str | None,
    system_prompt: str,
    model: str,
) -> tuple[str, str, float]:
    """claude -p 호출. (응답 텍스트, session_id, 소요초) 반환."""
    cmd = [
        "claude", "-p",
        "--dangerously-skip-permissions",
        "--model", model,
        "--system-prompt", system_prompt,
        "--output-format", "json",
        "--no-session-persistence",
        message,
    ]

    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd="/tmp")
    elapsed = time.time() - t0

    if result.returncode != 0:
        raise RuntimeError(f"Claude 오류: {result.stderr.strip()[:400]}")

    data = json.loads(result.stdout)
    return data["result"], data.get("session_id", ""), elapsed


# ── Codex 헬퍼 ────────────────────────────────────────────────────────────────

def call_codex(message: str, *, model: str) -> tuple[str, float]:
    """codex exec 헤드리스 stdin 모드 호출. (응답 텍스트, 소요초) 반환."""
    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise RuntimeError("codex CLI를 찾을 수 없습니다.")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        output_path = f.name

    cmd = [
        codex_bin, "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "-s", "read-only",
        "-m", model,
        "-o", output_path,
        "-",
    ]
    t0 = time.time()
    result = subprocess.run(
        cmd, input=message, capture_output=True, text=True, timeout=180,
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        Path(output_path).unlink(missing_ok=True)
        raise RuntimeError(f"Codex 오류: {result.stderr.strip()[:400]}")

    text = Path(output_path).read_text(encoding="utf-8").strip()
    Path(output_path).unlink(missing_ok=True)
    return text, elapsed


# ── 오케스트레이터 ────────────────────────────────────────────────────────────

def _print_banner(agenda: str, rounds: int, claude_model: str, codex_model: str, verbose: bool) -> None:
    claude_provider = "Anthropic"
    codex_provider = "OpenAI" if codex_model.startswith(("gpt", "o")) else "Unknown"
    print(f"\n{'═'*60}", flush=True)
    print(f"안건: {agenda}", flush=True)
    print(f"{'═'*60}", flush=True)
    print("■ 모델 정보", flush=True)
    print(f"  Claude : {claude_model:20s} ({claude_provider})", flush=True)
    print(f"  Codex  : {codex_model:20s} ({codex_provider})", flush=True)
    print("■ 실행 파라미터", flush=True)
    print(f"  rounds       = {rounds}", flush=True)
    print(f"  verbose      = {verbose}", flush=True)
    print(f"  claude-timeout = 900s / codex-timeout = 180s", flush=True)
    print(f"{'═'*60}\n", flush=True)


def run_debate(
    agenda: str,
    rounds: int = 3,
    claude_model: str = "sonnet",
    codex_model: str = "gpt-5.5",
    verbose: bool = True,
) -> str:
    history: list[tuple[str, str]] = []
    stats: list[tuple[str, float]] = []
    debate_start = time.time()

    def log(speaker: str, text: str, elapsed: float) -> None:
        if verbose:
            print(f"\n{'─'*60}\n[{speaker}]  ({elapsed:.1f}s)\n{'─'*60}\n{text}\n", flush=True)

    def status(step: str, current: int | None = None, total: int | None = None) -> None:
        bar = f"[라운드 {current}/{total}]" if current is not None else ""
        print(f"  ▶ {step} {bar}", flush=True)

    def build_prompt(message: str) -> str:
        if not history:
            return f"안건: {agenda}\n\n{message}"
        hist = "\n\n".join(f"[{s}] {m}" for s, m in history)
        return f"안건: {agenda}\n\n지금까지 대화:\n{hist}\n\n{message}"

    _print_banner(agenda, rounds, claude_model, codex_model, verbose)

    # ── 초기 입장 ────────────────────────────────────────────────────────────

    status("Claude 초기 입장 생성 중...")
    claude_msg, _, t = call_claude(
        build_prompt("당신의 초기 입장을 밝혀주세요."),
        session_id=None, system_prompt=CLAUDE_SYSTEM, model=claude_model,
    )
    stats.append(("Claude 초기입장", t))
    log("Claude (초기 입장)", claude_msg, t)
    history.append(("Claude", claude_msg))

    codex_opening = (
        f"{CODEX_SYSTEM}\n\n안건: {agenda}\n\n"
        f"Claude의 초기 입장:\n{claude_msg}\n\n당신의 초기 입장을 밝혀주세요."
    )
    status("Codex 초기 입장 생성 중...")
    codex_msg, t = call_codex(codex_opening, model=codex_model)
    stats.append(("Codex 초기입장", t))
    log("Codex (초기 입장)", codex_msg, t)
    history.append(("Codex", codex_msg))

    # ── 라운드 반복 ───────────────────────────────────────────────────────────

    for r in range(1, rounds + 1):
        last_note = "\n\n[마지막 라운드입니다. 최종 입장을 정리해주세요.]" if r == rounds else ""

        status("Claude 응답 생성 중...", r, rounds)
        claude_msg, _, t = call_claude(
            build_prompt(
                f"Codex의 방금 발언:\n{history[-1][1]}\n\n반론하거나 수렴 의견을 말해주세요.{last_note}"
            ),
            session_id=None, system_prompt=CLAUDE_SYSTEM, model=claude_model,
        )
        stats.append((f"Claude R{r}", t))
        log(f"Claude (라운드 {r})", claude_msg, t)
        history.append(("Claude", claude_msg))

        history_text = "\n\n".join(f"[{s}] {m}" for s, m in history)
        codex_prompt = (
            f"{CODEX_SYSTEM}\n\n안건: {agenda}\n\n지금까지 대화:\n{history_text}\n\n"
            f"Claude의 방금 발언에 대해 반론하거나 수렴 의견을 말해주세요.{last_note}"
        )
        status("Codex 응답 생성 중...", r, rounds)
        codex_msg, t = call_codex(codex_prompt, model=codex_model)
        stats.append((f"Codex R{r}", t))
        log(f"Codex (라운드 {r})", codex_msg, t)
        history.append(("Codex", codex_msg))

    # ── 결론 도출 ─────────────────────────────────────────────────────────────

    history_text = "\n\n".join(f"[{s}] {m}" for s, m in history)
    status("사회자 최종 결론 도출 중...")
    conclusion, _, t = call_claude(
        f"전체 토론 내용:\n{history_text}\n\n{MODERATOR_PROMPT}",
        session_id=None, system_prompt=MODERATOR_SYSTEM, model=claude_model,
    )
    stats.append(("사회자 결론", t))

    print(f"\n{'═'*60}", flush=True)
    print("[최종 결론]", flush=True)
    print(f"{'═'*60}\n{conclusion}\n{'═'*60}\n", flush=True)

    total_elapsed = time.time() - debate_start
    print("■ 소요 시간 통계", flush=True)
    for label, sec in stats:
        print(f"  {label:<15s}: {sec:6.1f}s", flush=True)
    print(f"  {'총 합계':<15s}: {total_elapsed:6.1f}s", flush=True)
    print(f"{'═'*60}\n", flush=True)

    return conclusion


# ── 진입점 ────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Claude vs Codex 헤드리스 회의 오케스트레이터")
    parser.add_argument("agenda", help="회의 안건 (예: '주 4일 근무제 도입 여부')")
    parser.add_argument("--rounds", type=int, default=3, help="토론 라운드 수 (기본 3)")
    parser.add_argument("--claude-model", default="sonnet", help="Claude 모델 (기본 sonnet)")
    parser.add_argument("--codex-model", default="gpt-5.5", help="Codex 모델 (기본 gpt-5.5)")
    parser.add_argument("--quiet", action="store_true", help="중간 발언 숨기고 결론만 출력")
    args = parser.parse_args()

    try:
        run_debate(
            agenda=args.agenda,
            rounds=args.rounds,
            claude_model=args.claude_model,
            codex_model=args.codex_model,
            verbose=not args.quiet,
        )
    except KeyboardInterrupt:
        print("\n중단됨.", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
