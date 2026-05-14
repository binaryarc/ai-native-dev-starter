#!/usr/bin/env python3
"""
PostToolUse hook: Write/Edit 후 변경된 파일을 분석해
Claude에게 어느 docs/ 문서를 갱신해야 하는지 additionalContext로 알려준다.
실제 갱신은 Claude가 판단해서 수행 — 강제 자동화 아님(오버엔지니어링 방지).
"""

import json
import sys
from pathlib import Path

# 변경 유형 → 갱신 대상 매핑
SYNC_RULES = [
    (
        lambda p: any(p.startswith(x) for x in ["src/", "lib/", "app/"]) and
                  any(p.endswith(x) for x in ["/router", "/api", "/endpoint", "/controller",
                                               "_router.py", "_api.py", "_endpoint.py",
                                               "Controller.java", "Router.go", "handler.go"]),
        "docs/api/INDEX.md",
        "API 엔드포인트 변경 감지 — 엔드포인트 추가·변경·삭제 내용을 docs/api/INDEX.md 에 반영하세요.",
    ),
    (
        lambda p: any(x in p for x in ["migration", "schema", "migrate", "alembic",
                                        "flyway", "liquibase", ".sql"]),
        "docs/database/INDEX.md",
        "DB 스키마·마이그레이션 변경 감지 — docs/database/INDEX.md 와 schema.md 를 갱신하세요.",
    ),
    (
        lambda p: any(x in p for x in ["component", "page", "screen", "view", "widget",
                                        ".tsx", ".jsx", "Component.", "Page.", "Screen."]) and
                  any(p.startswith(x) for x in ["src/", "frontend/", "web/", "ui/"]),
        "docs/design/INDEX.md",
        "UI 컴포넌트·화면 변경 감지 — docs/design/INDEX.md 를 갱신하세요.",
    ),
    (
        lambda p: any(x in p for x in ["src/", "lib/", "app/", "pkg/", "internal/"]) and
                  not any(x in p for x in ["test_", "_test.", ".test.", ".spec.", "Test.", "Spec."]),
        "MAP.md",
        "소스 파일 변경 감지 — MAP.md 소스 코드 인덱스의 심볼·설명을 갱신하세요.",
    ),
]


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # PostToolUse 이벤트만 처리
    if hook_input.get("hook_event_name") != "PostToolUse":
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in {"Write", "Edit"}:
        sys.exit(0)

    file_path = hook_input.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    cwd = hook_input.get("cwd", ".")
    root = Path(cwd).resolve()

    # 절대→상대 경로로 정규화
    try:
        rel = str(Path(file_path).resolve().relative_to(root))
    except ValueError:
        rel = file_path

    # docs/ 자신 변경은 무시 (무한 루프 방지)
    if rel.startswith("docs/") or rel.startswith(".claude/"):
        sys.exit(0)

    # 매칭 규칙 수집
    triggered = []
    for matcher, target, message in SYNC_RULES:
        if matcher(rel):
            triggered.append((target, message))

    if not triggered:
        sys.exit(0)

    # 중복 제거 (MAP.md 가 여러 규칙에 걸릴 수 있음)
    seen = set()
    unique = []
    for t in triggered:
        if t[0] not in seen:
            seen.add(t[0])
            unique.append(t)

    targets = ", ".join(t for t, _ in unique)
    messages = "\n".join(f"- {m}" for _, m in unique)

    # history 항목은 항상 추가
    today_history = f"docs/history/$(date +%Y%m%d).md"
    history_msg = f"- 코드 변경 이력을 {today_history} 에 추가하세요."

    context = (
        f"[doc-sync] {rel} 변경 후 갱신 필요:\n"
        f"{messages}\n"
        f"{history_msg}\n"
        f"\n갱신 방법: /doc-sync {rel}"
    )

    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
