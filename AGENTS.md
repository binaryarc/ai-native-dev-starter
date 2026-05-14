---
name: agents-context
description: >
  OpenAI Codex 에이전트 행동 지침. 코딩 원칙, 파일 탐색 방법, 스킬 사용법,
  TDD 원칙, 컨텍스트 파일 200줄 제한 등 모든 작업에 적용되는 기본 규칙.
type: context
load: always
---

# AGENTS.md

이 프로젝트의 Codex 에이전트 행동 지침.
CLAUDE.md 와 동일한 원칙을 적용하며, Codex 전용 실행 방식을 명시한다.

## 1. 코딩 전에 생각하기

- 가정을 명시적으로 밝혀라. 불확실하면 질문하라.
- 해석이 여러 가지라면 제시하라 — 조용히 하나를 고르지 마라.
- 더 단순한 접근법이 있다면 말하라.
- 불명확한 것이 있으면 멈추고 질문하라.

## 2. 단순함 우선

- 요청받지 않은 기능은 추가하지 않는다.
- 단일 용도 코드에 추상화를 만들지 않는다.
- 200줄로 짠 코드가 50줄로 가능하면 다시 작성한다.

## 3. 외과적 변경

- 반드시 필요한 것만 건드린다.
- 관련 없는 코드·주석·포매팅을 "개선"하지 않는다.
- 자신의 변경으로 불필요해진 import/변수만 제거한다.

## 4. TDD 원칙

`src/` 에 소스 파일을 작성하기 전에 반드시 테스트 파일을 먼저 작성한다.

```
Red   → 실패하는 테스트 작성
Green → 테스트를 통과하는 최소 구현
Refactor → 동작을 유지하며 정리
```

언어별 테스트 명령 → `docs` 섹션의 lang-profiles 참조.

## 5. 파일 탐색

파일·심볼·문서 위치는 **MAP.md** 를 먼저 읽어라.
2홉 이내에 모든 목적지에 도달할 수 있다.

```
홉 1: MAP.md 읽기
홉 2: MAP.md 링크 따라 목적지 도달
```

## 6. 컨텍스트 파일 200줄 제한

AGENTS.md, CLAUDE.md, GEMINI.md 는 200줄을 초과하지 않는다.
상세 내용은 별도 파일로 분리하고 이 파일에서 참조한다.

---

## 스킬 참조

이 프로젝트의 스킬은 `.claude/skills/` 에 있다.
Codex는 스킬을 직접 호출할 수 없으므로, 아래 방법으로 스킬 내용을 참조한다:

```bash
cat .claude/skills/<skill-name>/SKILL.md
```

| 스킬 | 파일 | 용도 |
|---|---|---|
| loop-work | `.claude/skills/loop-work/SKILL.md` | 개발→테스트→배포 루프 |
| tdd | `.claude/skills/tdd/SKILL.md` | Red→Green→Refactor 절차 |
| debate | `.claude/skills/debate/SKILL.md` | Claude vs Codex 토론 |
| doc-sync | `.claude/skills/doc-sync/SKILL.md` | 코드 변경 후 docs/ 갱신 |
| ai-ready-score | `.claude/skills/ai-ready-score/SKILL.md` | AI 준비도 감사 |
| nav | `.claude/skills/nav/SKILL.md` | MAP.md 기반 2홉 파일 탐색 |
| frontmatter | `.claude/skills/frontmatter/SKILL.md` | md 문서 frontmatter 작성 규칙 |

언어별 빌드·테스트·배포 명령:
```bash
cat .claude/skills/loop-work/lang-profiles.md
```

---

## docs/ 구조

```
docs/
├── architecture/INDEX.md  ← 시스템 구조
├── database/INDEX.md      ← 스키마·마이그레이션
├── design/INDEX.md        ← UI/UX 명세
├── tacit/INDEX.md         ← 암묵지·운영 노하우
├── api/INDEX.md           ← API 엔드포인트 명세
├── adr/INDEX.md           ← 아키텍처 결정 기록
└── history/INDEX.md       ← 날짜별 변경 이력
```

코드 변경 후 관련 docs/INDEX.md 를 갱신한다.
갱신 기준은 `.claude/skills/doc-sync/SKILL.md` 참조.

---

## Git 훅

```bash
bash hooks/install-hooks.sh   # 최초 1회 실행
```

설치 후 `git commit` 시 자동 실행:
1. `hooks/pre-commit` — lint·test·build
2. `hooks/pre-commit-review` — sub-agent diff 보안·성능·컨벤션 리뷰
