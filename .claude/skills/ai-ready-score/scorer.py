#!/usr/bin/env python3
"""AI-Ready Score: 코드베이스를 7카테고리 루브릭으로 감사해 JSON + HTML 보고서를 산출한다."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


# ── 루브릭 로드 ───────────────────────────────────────────────────────────────

def load_rubric(rubric_path: Path) -> dict:
    with rubric_path.open(encoding="utf-8") as f:
        return json.load(f)


# ── 체크 메서드 구현 ──────────────────────────────────────────────────────────

def _glob_any(root: Path, patterns: list[str]) -> bool:
    for pattern in patterns:
        if "**" in pattern:
            if list(root.glob(pattern)):
                return True
        else:
            if (root / pattern).exists():
                return True
    return False


def check_file_exists(root: Path, check: dict) -> tuple[int, str]:
    targets = check.get("targets", [])
    found = [t for t in targets if (root / t).exists()]
    if found:
        return check["points"], f"발견: {found[0]}"
    return 0, f"없음: {targets}"


def check_file_content_length(root: Path, check: dict) -> tuple[int, str]:
    targets = check.get("targets", [])
    min_chars = check.get("min_chars", 0)
    min_lines = check.get("min_lines", 0)

    for t in targets:
        p = root / t
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if min_chars and len(text) >= min_chars:
            return check["points"], f"{t}: {len(text)}자"
        if min_lines and len(text.splitlines()) >= min_lines:
            return check["points"], f"{t}: {len(text.splitlines())}줄"
        # partial
        if check.get("partial"):
            if min_chars and len(text) > 0:
                return check.get("partial_points", 0), f"{t}: {len(text)}자 (부분 점수)"
            if min_lines and len(text.splitlines()) > 0:
                return check.get("partial_points", 0), f"{t}: {len(text.splitlines())}줄 (부분 점수)"
    return 0, f"없음 또는 분량 부족: {targets}"


def check_file_line_limit(root: Path, check: dict) -> tuple[int, str]:
    targets = check.get("targets", [])
    max_lines = check.get("max_lines", 200)
    found = [t for t in targets if (root / t).exists()]
    if not found:
        return check["points"], "해당 파일 없음 (적용 불필요)"
    violations = []
    for t in found:
        lines = len((root / t).read_text(encoding="utf-8", errors="ignore").splitlines())
        if lines > max_lines:
            violations.append(f"{t}: {lines}줄")
    if violations:
        return 0, f"초과: {', '.join(violations)}"
    return check["points"], f"모두 {max_lines}줄 이내"


def check_file_exists_pattern(root: Path, check: dict) -> tuple[int, str]:
    patterns = check.get("patterns", [])
    if _glob_any(root, patterns):
        return check["points"], f"패턴 매칭 성공"
    return 0, f"패턴 없음: {patterns[:2]}..."


def check_dir_exists(root: Path, check: dict) -> tuple[int, str]:
    targets = check.get("targets", [])
    found = [t for t in targets if (root / t).is_dir()]
    if found:
        return check["points"], f"발견: {found[0]}/"
    return 0, f"없음: {targets}"


def check_avg_file_lines(root: Path, check: dict) -> tuple[int, str]:
    extensions = check.get("extensions", [".py"])
    max_avg = check.get("max_avg_lines", 300)
    files = []
    for ext in extensions:
        files.extend(root.rglob(f"*{ext}"))
    # 숨김 디렉토리, node_modules, .git 제외
    files = [f for f in files if not any(
        part.startswith(".") or part in {"node_modules", "__pycache__", "dist", "build", "target"}
        for part in f.parts
    )]
    if not files:
        return check["points"], "소스 파일 없음 (적용 불필요)"
    line_counts = []
    for f in files:
        try:
            line_counts.append(len(f.read_text(encoding="utf-8", errors="ignore").splitlines()))
        except Exception:
            pass
    if not line_counts:
        return check["points"], "읽기 불가"
    avg = sum(line_counts) / len(line_counts)
    if avg <= max_avg:
        return check["points"], f"평균 {avg:.0f}줄 ({len(files)}개 파일)"
    partial_threshold = check.get("partial_threshold", max_avg * 2)
    if check.get("partial") and avg <= partial_threshold:
        return check.get("partial_points", 0), f"평균 {avg:.0f}줄 (부분 점수)"
    return 0, f"평균 {avg:.0f}줄 > {max_avg}줄 기준 초과"


def check_no_large_files(root: Path, check: dict) -> tuple[int, str]:
    extensions = check.get("extensions", [".py"])
    max_lines = check.get("max_lines", 1000)
    violations = []
    for ext in extensions:
        for f in root.rglob(f"*{ext}"):
            if any(part.startswith(".") or part in {"node_modules", "__pycache__", "dist", "build", "target"}
                   for part in f.parts):
                continue
            try:
                n = len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
                if n > max_lines:
                    violations.append(f"{f.relative_to(root)}: {n}줄")
            except Exception:
                pass
    if violations:
        sample = violations[:3]
        return 0, f"{len(violations)}개 파일 초과: {', '.join(sample)}"
    return check["points"], f"모든 파일 {max_lines}줄 이내"


def check_test_files_exist(root: Path, check: dict) -> tuple[int, str]:
    patterns = check.get("patterns", [])
    min_count = check.get("min_count", 1)
    found = []
    for pattern in patterns:
        found.extend(root.rglob(pattern))
    found = [f for f in found if not any(
        part in {"node_modules", "__pycache__", "dist", "build", "target", ".git"}
        for part in f.parts
    )]
    if len(found) >= min_count:
        return check["points"], f"테스트 파일 {len(found)}개 발견"
    return 0, f"테스트 파일 없음"


def check_test_ratio(root: Path, check: dict) -> tuple[int, str]:
    min_ratio = check.get("min_ratio", 0.3)
    src_exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs"}
    test_patterns = {"test_*", "*_test.*", "*.test.*", "*.spec.*", "*Test.*", "*Spec.*"}

    all_files = []
    for ext in src_exts:
        all_files.extend(root.rglob(f"*{ext}"))
    all_files = [f for f in all_files if not any(
        part.startswith(".") or part in {"node_modules", "__pycache__", "dist", "build", "target"}
        for part in f.parts
    )]

    test_files = [
        f for f in all_files
        if any(fnmatch.fnmatch(f.name, p) for p in test_patterns)
        or any(part in {"tests", "test", "__tests__", "spec"} for part in f.parts)
    ]
    src_files = [f for f in all_files if f not in test_files]

    if not src_files:
        return check["points"], "소스 파일 없음 (적용 불필요)"

    ratio = len(test_files) / len(src_files)
    if ratio >= min_ratio:
        return check["points"], f"테스트 비율 {ratio:.0%} (src:{len(src_files)} test:{len(test_files)})"
    partial_threshold = check.get("partial_threshold", 0.1)
    if check.get("partial") and ratio >= partial_threshold:
        return check.get("partial_points", 0), f"테스트 비율 {ratio:.0%} (부분 점수)"
    return 0, f"테스트 비율 {ratio:.0%} < {min_ratio:.0%} 기준 미달"


def check_gitignore_contains(root: Path, check: dict) -> tuple[int, str]:
    gi = root / ".gitignore"
    if not gi.exists():
        return 0, ".gitignore 없음"
    content = gi.read_text(encoding="utf-8", errors="ignore")
    patterns = check.get("patterns", [".env"])
    found = [p for p in patterns if p in content]
    if found:
        return check["points"], f".gitignore에 {found} 포함"
    return 0, f".gitignore에 {patterns} 미포함"


def check_no_hardcoded_secrets(root: Path, check: dict) -> tuple[int, str]:
    secret_patterns = [re.compile(p) for p in check.get("secret_patterns", [])]
    exclude_patterns = check.get("exclude_patterns", [])
    violations = []

    for ext in [".py", ".ts", ".js", ".java", ".go", ".env", ".yml", ".yaml", ".json", ".toml"]:
        for f in root.rglob(f"*{ext}"):
            if any(part.startswith(".") or part in {"node_modules", "__pycache__", "dist", "build", "target", ".git"}
                   for part in f.parts):
                continue
            if any(fnmatch.fnmatch(f.name, ep) for ep in exclude_patterns):
                continue
            if any(fnmatch.fnmatch(str(f.relative_to(root)), ep) for ep in exclude_patterns):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for pattern in secret_patterns:
                    match = pattern.search(content)
                    if match:
                        rel = f.relative_to(root)
                        violations.append(str(rel))
                        break
            except Exception:
                pass

    if violations:
        sample = violations[:3]
        return 0, f"시크릿 의심 패턴 {len(violations)}개 파일: {', '.join(sample)}"
    return check["points"], "하드코딩 시크릿 미탐지"


def check_commit_message_quality(root: Path, check: dict) -> tuple[int, str]:
    sample = check.get("sample", 10)
    min_avg_len = check.get("min_avg_len", 20)
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={sample}", "--format=%s"],
            capture_output=True, text=True, cwd=root, timeout=10,
        )
        messages = [m.strip() for m in result.stdout.strip().splitlines() if m.strip()]
        if not messages:
            return 0, "커밋 없음"
        avg_len = sum(len(m) for m in messages) / len(messages)
        if avg_len >= min_avg_len:
            return check["points"], f"평균 {avg_len:.0f}자 ({len(messages)}개 커밋)"
        partial_threshold = check.get("partial_threshold", 10)
        if check.get("partial") and avg_len >= partial_threshold:
            return check.get("partial_points", 0), f"평균 {avg_len:.0f}자 (부분 점수)"
        return 0, f"평균 {avg_len:.0f}자 < {min_avg_len}자 기준 미달"
    except Exception as e:
        return 0, f"git log 실패: {e}"


def check_conventional_commits(root: Path, check: dict) -> tuple[int, str]:
    sample = check.get("sample", 20)
    min_ratio = check.get("min_ratio", 0.5)
    conventional = re.compile(
        r"^(feat|fix|chore|docs|style|refactor|test|perf|ci|build|revert)(\(.+\))?!?:"
    )
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={sample}", "--format=%s"],
            capture_output=True, text=True, cwd=root, timeout=10,
        )
        messages = [m.strip() for m in result.stdout.strip().splitlines() if m.strip()]
        if not messages:
            return 0, "커밋 없음"
        matched = [m for m in messages if conventional.match(m)]
        ratio = len(matched) / len(messages)
        if ratio >= min_ratio:
            return check["points"], f"컨벤셔널 커밋 {ratio:.0%} ({len(matched)}/{len(messages)})"
        partial_threshold = check.get("partial_threshold", 0.2)
        if check.get("partial") and ratio >= partial_threshold:
            return check.get("partial_points", 0), f"컨벤셔널 커밋 {ratio:.0%} (부분 점수)"
        return 0, f"컨벤셔널 커밋 {ratio:.0%} < {min_ratio:.0%} 기준 미달"
    except Exception as e:
        return 0, f"git log 실패: {e}"


# ── 디스패처 ──────────────────────────────────────────────────────────────────

CHECK_METHODS = {
    "file_exists": check_file_exists,
    "file_content_length": check_file_content_length,
    "file_line_limit": check_file_line_limit,
    "file_exists_pattern": check_file_exists_pattern,
    "dir_exists": check_dir_exists,
    "avg_file_lines": check_avg_file_lines,
    "no_large_files": check_no_large_files,
    "test_files_exist": check_test_files_exist,
    "test_ratio": check_test_ratio,
    "gitignore_contains": check_gitignore_contains,
    "no_hardcoded_secrets": check_no_hardcoded_secrets,
    "commit_message_quality": check_commit_message_quality,
    "conventional_commits": check_conventional_commits,
}


def run_check(root: Path, check: dict) -> dict:
    method = check.get("method")
    fn = CHECK_METHODS.get(method)
    if fn is None:
        return {"id": check["id"], "name": check["name"], "points": 0, "max": check["points"], "detail": f"알 수 없는 메서드: {method}"}
    earned, detail = fn(root, check)
    return {
        "id": check["id"],
        "name": check["name"],
        "earned": earned,
        "max": check["points"],
        "passed": earned > 0,
        "detail": detail,
    }


# ── 스코어링 ─────────────────────────────────────────────────────────────────

def score_repo(root: Path, rubric: dict) -> dict:
    results = {"categories": [], "total_earned": 0, "total_max": rubric["total"]}

    for cat in rubric["categories"]:
        cat_result = {
            "id": cat["id"],
            "name": cat["name"],
            "name_ko": cat["name_ko"],
            "description": cat["description"],
            "max_score": cat["max_score"],
            "earned": 0,
            "checks": [],
        }
        for check in cat["checks"]:
            r = run_check(root, check)
            cat_result["checks"].append(r)
            cat_result["earned"] += r["earned"]
        results["categories"].append(cat_result)
        results["total_earned"] += cat_result["earned"]

    # 등급 산출
    score = results["total_earned"]
    grade = "F"
    for g, threshold in sorted(rubric["grade_thresholds"].items(), key=lambda x: -x[1]):
        if score >= threshold:
            grade = g
            break
    results["grade"] = grade
    results["grade_label"] = rubric["grade_labels"].get(grade, "")
    results["repo_path"] = str(root.resolve())
    results["scored_at"] = str(date.today())

    return results


# ── ROI 액션 리스트 ───────────────────────────────────────────────────────────

ROI_ACTIONS = {
    "C1-1": ("CLAUDE.md 생성 (AI 컨텍스트 파일)", "high", 30),
    "C1-2": ("README.md 작성 (200자 이상)", "high", 20),
    "C1-3": ("docs/architecture.md 작성", "medium", 60),
    "C1-4": ("컨텍스트 파일 200줄 이내로 정리", "high", 20),
    "C1-5": ("CHANGELOG.md 또는 docs/history/ 생성", "low", 30),
    "C1-6": ("docs/todo.md 생성", "low", 10),
    "C2-1": ("src/ 소스 디렉토리 구조 정리", "medium", 120),
    "C2-2": ("대형 파일 분할 (평균 300줄 이하로)", "medium", 240),
    "C2-3": ("1000줄 초과 파일 분할", "high", 120),
    "C2-4": ("tests/ 디렉토리 분리", "high", 60),
    "C2-5": (".env.example 및 설정 파일 분리", "high", 30),
    "C3-1": ("기본 단위 테스트 추가", "high", 240),
    "C3-2": ("테스트 커버리지 30% 이상으로 확대", "medium", 480),
    "C3-3": ("GitHub Actions CI 파이프라인 추가", "high", 60),
    "C3-4": ("커버리지 측정 설정 추가 (pytest-cov 등)", "medium", 30),
    "C4-1": (".claude/ 디렉토리 및 설정 생성", "high", 15),
    "C4-2": ("AI 스킬/룰 정의 파일 작성", "high", 60),
    "C4-3": (".cursorignore / .claudeignore 추가", "low", 10),
    "C4-4": ("MCP 서버 또는 AI 도구 설정 파일 추가", "medium", 30),
    "C4-5": ("AI 실수 기록 docs/ai-mistakes/ 생성", "medium", 30),
    "C5-1": ("lockfile 커밋 (uv.lock, package-lock.json 등)", "high", 15),
    "C5-2": (".env.example 생성 (환경변수 문서화)", "high", 20),
    "C5-3": ("Dockerfile 또는 docker-compose.yml 추가", "medium", 120),
    "C6-1": (".gitignore 충분히 구성 (10줄 이상)", "high", 20),
    "C6-2": ("커밋 메시지 길이 개선 (평균 20자 이상)", "medium", 0),
    "C6-3": ("GitHub PR 템플릿 추가 (.github/pull_request_template.md)", "medium", 20),
    "C6-4": ("컨벤셔널 커밋 규칙 도입 (feat/fix/chore:)", "medium", 0),
    "C7-1": (".gitignore에 .env 추가", "high", 5),
    "C7-2": ("하드코딩 시크릿 환경변수로 이전", "critical", 60),
    "C7-3": ("보안 스캔 도구 설정 추가 (bandit, semgrep 등)", "medium", 30),
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def build_action_list(results: dict) -> list[dict]:
    actions = []
    for cat in results["categories"]:
        for check in cat["checks"]:
            if not check["passed"]:
                cid = check["id"]
                if cid in ROI_ACTIONS:
                    desc, priority, effort_min = ROI_ACTIONS[cid]
                    actions.append({
                        "check_id": cid,
                        "category": cat["name_ko"],
                        "action": desc,
                        "priority": priority,
                        "effort_minutes": effort_min,
                        "points_gain": check["max"],
                        "current_detail": check["detail"],
                    })
    actions.sort(key=lambda x: (PRIORITY_ORDER.get(x["priority"], 9), -x["points_gain"], x["effort_minutes"]))
    return actions


# ── HTML 대시보드 ─────────────────────────────────────────────────────────────

def _grade_color(grade: str) -> str:
    return {"S": "#00b894", "A": "#00cec9", "B": "#fdcb6e", "C": "#e17055", "D": "#d63031", "F": "#2d3436"}.get(grade, "#636e72")


def _priority_badge(priority: str) -> str:
    colors = {"critical": "#d63031", "high": "#e17055", "medium": "#fdcb6e", "low": "#74b9ff"}
    labels = {"critical": "긴급", "high": "높음", "medium": "보통", "low": "낮음"}
    color = colors.get(priority, "#b2bec3")
    label = labels.get(priority, priority)
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">{label}</span>'


def generate_html(results: dict, actions: list[dict], rubric: dict) -> str:
    score = results["total_earned"]
    max_score = results["total_max"]
    grade = results["grade"]
    grade_label = results["grade_label"]
    grade_color = _grade_color(grade)
    repo_path = results["repo_path"]
    scored_at = results["scored_at"]

    # 카테고리 바
    cat_bars = ""
    for cat in results["categories"]:
        pct = int(cat["earned"] / cat["max_score"] * 100) if cat["max_score"] else 0
        color = "#00b894" if pct >= 80 else "#fdcb6e" if pct >= 50 else "#e17055"
        checks_html = "".join(
            f'<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f2f6">'
            f'<span style="color:{"#2d3436" if c["passed"] else "#b2bec3"};font-size:12px">'
            f'{"✅" if c["passed"] else "❌"} {c["name"]}</span>'
            f'<span style="font-size:12px;color:#636e72">{c["earned"]}/{c["max"]}점 — {c["detail"]}</span>'
            f'</div>'
            for c in cat["checks"]
        )
        cat_bars += f"""
        <div style="margin-bottom:20px;background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.08)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <div>
              <span style="font-weight:700;font-size:14px">{cat["id"]} {cat["name_ko"]}</span>
              <span style="color:#636e72;font-size:12px;margin-left:8px">{cat["description"]}</span>
            </div>
            <span style="font-weight:700;font-size:14px;color:{color}">{cat["earned"]}/{cat["max_score"]}점</span>
          </div>
          <div style="background:#f1f2f6;border-radius:4px;height:8px">
            <div style="background:{color};width:{pct}%;height:8px;border-radius:4px;transition:width .3s"></div>
          </div>
          <div style="margin-top:10px">{checks_html}</div>
        </div>"""

    # 액션 리스트
    action_rows = ""
    for i, a in enumerate(actions[:20], 1):
        effort = f"{a['effort_minutes']}분" if a["effort_minutes"] else "상시"
        action_rows += f"""
        <tr style="border-bottom:1px solid #f1f2f6">
          <td style="padding:10px 8px;font-size:13px;color:#636e72">{i}</td>
          <td style="padding:10px 8px">{_priority_badge(a["priority"])}</td>
          <td style="padding:10px 8px;font-size:13px;color:#2d3436">{a["action"]}</td>
          <td style="padding:10px 8px;font-size:13px;color:#636e72">{a["category"]}</td>
          <td style="padding:10px 8px;font-size:13px;font-weight:600;color:#00b894">+{a["points_gain"]}점</td>
          <td style="padding:10px 8px;font-size:13px;color:#636e72">{effort}</td>
        </tr>"""

    # 등급 범례
    grade_legend = ""
    for g, label in rubric["grade_labels"].items():
        threshold = rubric["grade_thresholds"][g]
        is_current = g == grade
        bg = grade_color if is_current else "#f1f2f6"
        fg = "#fff" if is_current else "#636e72"
        grade_legend += f'<div style="background:{bg};color:{fg};padding:6px 12px;border-radius:6px;font-size:12px;margin:2px"><strong>{g}</strong> {threshold}점+ — {label}</div>'

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI-Ready Score — {repo_path}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8f9fa; color: #2d3436; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 32px 16px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th {{ background: #f1f2f6; padding: 10px 8px; font-size: 12px; text-align: left; color: #636e72; }}
</style>
</head>
<body>
<div class="container">

  <!-- 헤더 -->
  <div style="background:{grade_color};color:#fff;border-radius:12px;padding:28px 32px;margin-bottom:24px">
    <div style="font-size:13px;opacity:.8;margin-bottom:4px">AI-Ready Score Audit</div>
    <div style="font-size:13px;opacity:.8;margin-bottom:12px">📁 {repo_path} &nbsp;·&nbsp; 📅 {scored_at}</div>
    <div style="display:flex;align-items:center;gap:24px">
      <div style="font-size:72px;font-weight:900;line-height:1">{grade}</div>
      <div>
        <div style="font-size:40px;font-weight:700">{score}<span style="font-size:20px;opacity:.7">/{max_score}</span></div>
        <div style="font-size:16px;opacity:.9;margin-top:4px">{grade_label}</div>
      </div>
    </div>
  </div>

  <!-- 등급 범례 -->
  <div style="background:#fff;border-radius:8px;padding:16px;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">
    <div style="font-weight:700;margin-bottom:10px;font-size:14px">등급 기준</div>
    <div style="display:flex;flex-wrap:wrap;gap:4px">{grade_legend}</div>
  </div>

  <!-- 카테고리별 점수 -->
  <div style="font-weight:700;font-size:16px;margin-bottom:12px">카테고리별 점수</div>
  {cat_bars}

  <!-- ROI 액션 리스트 -->
  <div style="font-weight:700;font-size:16px;margin:24px 0 12px">ROI 우선순위 액션 리스트</div>
  <div style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)">
    <table>
      <thead>
        <tr>
          <th>#</th><th>우선순위</th><th>액션</th><th>카테고리</th><th>점수 이득</th><th>예상 소요</th>
        </tr>
      </thead>
      <tbody>{action_rows}</tbody>
    </table>
  </div>

  <div style="margin-top:24px;font-size:12px;color:#b2bec3;text-align:center">
    Generated by AI-Ready Score · rubric v{rubric.get("version","1.0.0")}
  </div>
</div>
</body>
</html>"""


# ── 진입점 ────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="AI-Ready Score: 코드베이스 AI 준비도 감사")
    parser.add_argument("repo", nargs="?", default=".", help="감사할 리포지토리 경로 (기본: 현재 디렉토리)")
    parser.add_argument("--rubric", default=None, help="루브릭 JSON 경로 (기본: 스크립트와 같은 디렉토리의 rubric.json)")
    parser.add_argument("--out-json", default=None, help="JSON 결과 출력 경로 (기본: <repo>/ai-ready-score.json)")
    parser.add_argument("--out-html", default=None, help="HTML 결과 출력 경로 (기본: <repo>/ai-ready-score.html)")
    parser.add_argument("--json-only", action="store_true", help="JSON만 출력 (HTML 생략)")
    parser.add_argument("--quiet", action="store_true", help="진행 메시지 숨김")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    if not root.exists():
        print(f"오류: 경로 없음 — {root}", file=sys.stderr)
        return 1

    script_dir = Path(__file__).parent
    rubric_path = Path(args.rubric) if args.rubric else script_dir / "rubric.json"
    if not rubric_path.exists():
        print(f"오류: 루브릭 파일 없음 — {rubric_path}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"▶ 감사 대상: {root}", flush=True)
        print(f"▶ 루브릭: {rubric_path}", flush=True)

    rubric = load_rubric(rubric_path)
    results = score_repo(root, rubric)
    actions = build_action_list(results)
    results["actions"] = actions

    # JSON 출력
    json_path = Path(args.out_json) if args.out_json else root / "ai-ready-score.json"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.quiet:
        print(f"✅ JSON 저장: {json_path}", flush=True)

    # HTML 출력
    if not args.json_only:
        html = generate_html(results, actions, rubric)
        html_path = Path(args.out_html) if args.out_html else root / "ai-ready-score.html"
        html_path.write_text(html, encoding="utf-8")
        if not args.quiet:
            print(f"✅ HTML 저장: {html_path}", flush=True)

    # 콘솔 요약
    if not args.quiet:
        print(f"\n{'═'*50}", flush=True)
        print(f"  등급: {results['grade']}  점수: {results['total_earned']}/{results['total_max']}점", flush=True)
        print(f"  {results['grade_label']}", flush=True)
        print(f"{'─'*50}", flush=True)
        for cat in results["categories"]:
            bar = "█" * int(cat["earned"] / cat["max_score"] * 10) if cat["max_score"] else ""
            print(f"  {cat['id']} {cat['name_ko']:<22} {bar:<10} {cat['earned']:2}/{cat['max_score']}점", flush=True)
        print(f"{'─'*50}", flush=True)
        if actions:
            print(f"  상위 3개 액션:", flush=True)
            for a in actions[:3]:
                print(f"    [{a['priority'].upper()}] {a['action']} (+{a['points_gain']}점)", flush=True)
        print(f"{'═'*50}\n", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
