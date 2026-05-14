#!/usr/bin/env python3
"""
PreToolUse hook: src/ 에 소스 파일을 쓰기 전에 대응하는 테스트 파일이 존재하는지 확인한다.
테스트 파일이 없으면 Write/Edit 를 차단하고 만들어야 할 테스트 파일 경로를 알려준다.

적용 대상: src/ 하위의 소스 파일 (테스트 파일 자신은 제외)
"""

import json
import sys
from pathlib import Path

# ── 테스트 파일 판별 ──────────────────────────────────────────────────────────

TEST_INDICATORS = {
    "prefix": ["test_"],
    "suffix": ["_test", "_spec", ".test", ".spec"],
    "dirs":   {"tests", "test", "__tests__", "spec"},
}

def is_test_file(path: Path) -> bool:
    name = path.stem
    if any(name.startswith(p) for p in TEST_INDICATORS["prefix"]):
        return True
    if any(name.endswith(s) for s in TEST_INDICATORS["suffix"]):
        return True
    if TEST_INDICATORS["dirs"] & set(path.parts):
        return True
    return False


# ── 언어별 테스트 파일 후보 경로 생성 ────────────────────────────────────────

def candidate_test_paths(src_path: Path, root: Path) -> list[Path]:
    """src_path 에 대응하는 테스트 파일 후보 경로 목록을 반환한다."""
    ext   = src_path.suffix          # .py / .ts / .tsx / .java / .go ...
    stem  = src_path.stem            # e.g. "user_service"
    rel   = src_path.relative_to(root)  # e.g. src/api/user_service.py

    # src/ → tests/ 로 루트 교체
    parts = list(rel.parts)
    if parts[0] == "src":
        parts[0] = "tests"
    tests_mirror = root / Path(*parts)

    candidates = []

    if ext == ".py":
        candidates += [
            src_path.parent / f"test_{stem}.py",
            src_path.parent / f"{stem}_test.py",
            tests_mirror.parent / f"test_{stem}.py",
            tests_mirror.parent / f"{stem}_test.py",
            root / "tests" / f"test_{stem}.py",
        ]
    elif ext in {".ts", ".tsx"}:
        candidates += [
            src_path.parent / f"{stem}.test{ext}",
            src_path.parent / f"{stem}.spec{ext}",
            src_path.parent / "__tests__" / f"{stem}.test{ext}",
            root / "src" / "__tests__" / f"{stem}.test{ext}",
        ]
    elif ext in {".js", ".jsx"}:
        candidates += [
            src_path.parent / f"{stem}.test{ext}",
            src_path.parent / f"{stem}.spec{ext}",
            src_path.parent / "__tests__" / f"{stem}.test{ext}",
        ]
    elif ext == ".java":
        # src/main/java/... → src/test/java/...
        str_parts = str(rel).replace("src/main/java", "src/test/java")
        java_test = root / str_parts.replace(f"{stem}.java", f"{stem}Test.java")
        candidates += [
            java_test,
            src_path.parent / f"{stem}Test.java",
        ]
    elif ext == ".go":
        candidates += [
            src_path.parent / f"{stem}_test.go",
        ]
    else:
        # 기타: 같은 디렉토리의 test_* 또는 *_test 패턴
        candidates += [
            src_path.parent / f"test_{stem}{ext}",
            src_path.parent / f"{stem}_test{ext}",
        ]

    # 중복 제거, 순서 유지
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


# ── 테스트 존재 여부 확인 ─────────────────────────────────────────────────────

def test_file_exists(src_path: Path, root: Path) -> tuple[bool, list[Path]]:
    """(테스트 존재 여부, 후보 경로 목록) 반환."""
    candidates = candidate_test_paths(src_path, root)
    for c in candidates:
        if c.exists():
            return True, candidates
    return False, candidates


# ── deny 응답 생성 ────────────────────────────────────────────────────────────

def deny(reason: str, context: str = "") -> None:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    if context:
        out["hookSpecificOutput"]["additionalContext"] = context
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


def allow() -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }))
    sys.exit(0)


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        allow()
        return

    tool_name  = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    cwd        = hook_input.get("cwd", ".")

    # Write / Edit 만 대상
    if tool_name not in {"Write", "Edit"}:
        allow()
        return

    file_path_str = tool_input.get("file_path", "")
    if not file_path_str:
        allow()
        return

    root     = Path(cwd).resolve()
    src_path = Path(file_path_str)
    if not src_path.is_absolute():
        src_path = (root / src_path).resolve()

    # src/ 하위가 아니면 통과
    try:
        src_path.relative_to(root / "src")
    except ValueError:
        allow()
        return

    # 테스트 파일 자신이면 통과
    if is_test_file(src_path):
        allow()
        return

    # 확장자 필터: 소스 코드 파일만 검사
    SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs", ".kt"}
    if src_path.suffix not in SOURCE_EXTS:
        allow()
        return

    # 테스트 파일 존재 확인
    exists, candidates = test_file_exists(src_path, root)
    if exists:
        allow()
        return

    # ── 차단 ──────────────────────────────────────────────────────────────────

    rel_src = src_path.relative_to(root) if src_path.is_relative_to(root) else src_path
    primary = candidates[0].relative_to(root) if candidates and candidates[0].is_relative_to(root) else (candidates[0] if candidates else Path("tests/") / f"test_{src_path.name}")

    reason = (
        f"TDD 위반: 테스트 파일 없음\n"
        f"  소스:  {rel_src}\n"
        f"  필요:  {primary}\n"
        f"먼저 테스트 파일을 작성하세요 (Red 단계)."
    )

    other_candidates = [
        str(c.relative_to(root)) if c.is_relative_to(root) else str(c)
        for c in candidates[1:3]
    ]
    context = (
        f"TDD Red-Green-Refactor: {rel_src} 을 작성하기 전에 "
        f"{primary} 를 먼저 만들고 실패하는 테스트를 작성하세요.\n"
        + (f"다른 허용 위치: {', '.join(other_candidates)}" if other_candidates else "")
    )

    deny(reason, context)


if __name__ == "__main__":
    main()
