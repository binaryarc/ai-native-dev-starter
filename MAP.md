---
name: project-map
description: >
  프로젝트 전체 파일 지도. 2홉 이내에 모든 문서·코드·스킬·설정에 도달할 수 있는
  단일 진입점. grep 없이 파일 위치를 찾을 때 참조.
  "어디 있어?", "파일 찾아줘", "구조 보여줘", "/nav" 호출 시 로드.
type: index
load: on-demand
updated: 2026-05-15

---

# Project Map

> 이 파일이 **홉 1**이다. 여기서 링크를 한 번 따라가면 **홉 2** — 목적지다.
> grep·find 없이 이 파일만 읽으면 어디든 도달할 수 있다.

---

## 에이전트 진입점 (항상 로드)

| 파일 | 역할 |
|---|---|
| [CLAUDE.md](./CLAUDE.md) | Claude Code 행동 지침 (코딩 원칙, 200줄 제한) |
| [AGENTS.md](./AGENTS.md) | Codex 에이전트 행동 지침 (동일 원칙 + Codex 전용) |
| [MAP.md](./MAP.md) | **이 파일** — 프로젝트 전체 지도 |

---

## .claude/ — AI 에이전트 설정

### rules/ — 항상 적용되는 원칙 (`load: always`)

| 파일 | 내용 |
|---|---|
| [.claude/rules/tdd.md](./.claude/rules/tdd.md) | TDD 원칙 — 테스트 먼저, Red→Green→Refactor |

### skills/ — 호출 가능한 스킬 (`load: on-demand`)

| 스킬 | 호출 | 파일 | 부속 파일 |
|---|---|---|---|
| debate | `/debate <안건>` | [SKILL.md](./.claude/skills/debate/SKILL.md) | [debate.py](./.claude/skills/debate/debate.py) |
| loop-work | `/loop-work <작업>` | [SKILL.md](./.claude/skills/loop-work/SKILL.md) | [lang-profiles.md](./.claude/skills/loop-work/lang-profiles.md) |
| ai-ready-score | `/ai-ready-score [경로]` | [SKILL.md](./.claude/skills/ai-ready-score/SKILL.md) | [scorer.py](./.claude/skills/ai-ready-score/scorer.py) · [rubric.json](./.claude/skills/ai-ready-score/rubric.json) |
| tdd | `/tdd <기능>` | [SKILL.md](./.claude/skills/tdd/SKILL.md) | — |
| frontmatter | `/frontmatter` | [SKILL.md](./.claude/skills/frontmatter/SKILL.md) | — |
| nav | `/nav <키워드>` | [SKILL.md](./.claude/skills/nav/SKILL.md) | — |
| doc-sync | `/doc-sync [파일]` | [SKILL.md](./.claude/skills/doc-sync/SKILL.md) | — |

> 전체 스킬 목록: [.claude/skills/SKILLS.md](./.claude/skills/SKILLS.md)

---

## docs/ — 프로젝트 문서

각 디렉토리의 `INDEX.md` 가 홉 2 진입점이다.

| 디렉토리 | INDEX.md | 용도 |
|---|---|---|
| `docs/architecture/` | [INDEX.md](./docs/architecture/INDEX.md) | 시스템 구조, 레이어, 컴포넌트 관계 |
| `docs/database/` | [INDEX.md](./docs/database/INDEX.md) | 스키마, 마이그레이션 이력, ERD |
| `docs/design/` | [INDEX.md](./docs/design/INDEX.md) | UI/UX 명세, 화면 설계, 컴포넌트 가이드 |
| `docs/tacit/` | [INDEX.md](./docs/tacit/INDEX.md) | 암묵지, 운영 노하우, 삽질 기록 |
| `docs/api/` | [INDEX.md](./docs/api/INDEX.md) | 엔드포인트 명세, 요청/응답 스키마 |
| `docs/adr/` | [INDEX.md](./docs/adr/INDEX.md) | Architecture Decision Records |
| `docs/history/` | [INDEX.md](./docs/history/INDEX.md) | 날짜별 변경 이력 (YYYYMMDD.md) |

---

## src/ — 소스 코드

> 현재 비어있음. 아래 구조로 채워간다.

```
src/
├── <package>/
│   ├── __init__.py
│   ├── core/        ← 핵심 비즈니스 로직
│   ├── api/         ← API 레이어
│   └── utils/       ← 유틸리티
└── tests/
    ├── unit/
    └── integration/
```

*파일이 생성되면 아래 [소스 코드 인덱스](#소스-코드-인덱스) 섹션에 추가한다.*

---

## templates/ — 프롬프트 템플릿

> 현재 비어있음.

```
templates/
├── feature-request-prompt.md
├── bug-fix-prompt.md
├── refactor-prompt.md
└── pr-description.md
```

---

## checklists/ — 체크리스트

> 현재 비어있음.

```
checklists/
├── before-agent-work.md
└── before-merge.md
```

---

## .claude/hooks/ — Claude Code PreToolUse 훅

| 파일 | 역할 |
|---|---|
| [.claude/hooks/tdd-guard.py](./.claude/hooks/tdd-guard.py) | PreToolUse: `src/` 소스 파일 쓰기 전 테스트 파일 존재 확인. 없으면 차단 |
| [.claude/hooks/doc-sync-trigger.py](./.claude/hooks/doc-sync-trigger.py) | PostToolUse: 소스 파일 변경 후 갱신 필요한 docs/ 문서를 Claude에게 알림 |
| [.claude/settings.json](./.claude/settings.json) | PreToolUse(tdd-guard) + PostToolUse(doc-sync-trigger) hook 등록 |

> 지원 언어: Python, TypeScript, JavaScript, Java, Go, Rust, Kotlin

---

## hooks/ — Git 훅

| 파일 | 역할 |
|---|---|
| [hooks/pre-commit](./hooks/pre-commit) | 커밋 직전 lint→test→build 자동 실행 후 review 훅 호출. 실패 시 커밋 차단 |
| [hooks/pre-commit-review](./hooks/pre-commit-review) | sub-agent(claude -p)가 diff만 보고 보안·성능·컨벤션 위반 탐지. BLOCK 시 커밋 차단 |
| [hooks/install-hooks.sh](./hooks/install-hooks.sh) | `.git/hooks/`에 심볼릭 링크 설치 (`bash hooks/install-hooks.sh`) |

> 스택 자동 감지: `pyproject.toml` → Python/ruff/pytest, `pom.xml` → Maven,
> `build.gradle` → Gradle, `package.json` → Node.js/React, `Makefile` → Make

---

## 설정 파일

| 파일 | 역할 |
|---|---|
| [README.md](./README.md) | 프로젝트 소개 및 시작 방법 |
| [.gitignore](./.gitignore) | Git 추적 제외 목록 |
| `.agents` | (비어있음) Codex 에이전트 설정 예정 |
| `.codex` | (비어있음) Codex 설정 예정 |

---

## 소스 코드 인덱스

> `src/` 파일이 생성될 때마다 아래 표에 추가한다.
> 형식: `파일경로 | 주요 함수·클래스 | 한 줄 설명`

| 파일 | 심볼 | 설명 |
|---|---|---|
| — | — | 아직 소스 코드 없음 |

---

## 문서 인덱스

> `docs/` 파일이 생성될 때마다 아래 표에 추가한다.

| 파일 | 핵심 키워드 | 설명 |
|---|---|---|
| — | — | 아직 문서 없음 |

---

## MAP 업데이트 규칙

새 파일을 추가할 때 이 파일을 함께 업데이트한다:

- **새 스킬** → skills/ 표에 행 추가
- **새 rule** → rules/ 표에 행 추가
- **새 docs/ 파일** → 문서 인덱스에 행 추가
- **새 src/ 파일** → 소스 코드 인덱스에 행 추가
- **새 template/checklist** → 해당 섹션 링크 추가
- `updated:` 날짜를 오늘로 갱신
