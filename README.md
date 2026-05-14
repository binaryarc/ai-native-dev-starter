---
name: project-readme
description: >
  AI 네이티브 개발 스타터팩 프로젝트 개요. Claude Code, Codex 등 AI 에이전트를
  개발 워크플로의 기본 단위로 사용하기 위한 스킬, 훅, 문서 구조 모음.
  프로젝트 구조와 시작 방법을 파악할 때 참조.
type: context
load: on-demand
---

# AI Native Dev Starter

AI 코딩 에이전트(Claude Code, Codex, Cursor 등)를 보조 도구가 아니라
**개발 워크플로의 기본 단위**로 쓰기 위한 스타터팩입니다.

복사해서 바로 쓸 수 있는 스킬, Git 훅, 문서 구조, 컨텍스트 파일을 제공합니다.

## Who This Is For

- AI 에이전트로 기능 구현, 리팩터링, 테스트, 리뷰를 반복하려는 개발자
- Claude Code, Codex, Cursor를 팀 워크플로에 붙이려는 팀
- 에이전트가 컨텍스트를 잃지 않고 일관되게 동작하는 구조를 원하는 사람

## 핵심 구성

### 에이전트 컨텍스트
| 파일 | 대상 | 역할 |
|---|---|---|
| [CLAUDE.md](./CLAUDE.md) | Claude Code | 코딩 원칙 5개, 200줄 제한 |
| [AGENTS.md](./AGENTS.md) | Codex | 동일 원칙 + Codex 전용 스킬 참조 방식 |
| [MAP.md](./MAP.md) | 모든 에이전트 | 2홉 프로젝트 지도 — grep 없이 모든 파일 도달 |

### 스킬 (`.claude/skills/`)
| 스킬 | 호출 | 설명 |
|---|---|---|
| `loop-work` | `/loop-work` | 개발→빌드→테스트→배포 루프 (13개 언어 스택) |
| `tdd` | `/tdd` | Red→Green→Refactor 언어별 명령 |
| `debate` | `/debate` | Claude vs Codex 헤드리스 토론으로 설계 결정 |
| `ai-ready-score` | `/ai-ready-score` | 코드베이스 AI 준비도 100점 루브릭 감사 |
| `doc-sync` | `/doc-sync` | 코드 변경 후 docs/ 자동 동기화 |
| `nav` | `/nav` | MAP.md 기반 2홉 파일 탐색 |
| `frontmatter` | `/frontmatter` | md 문서 lazy-loading frontmatter 작성 |

### 자동화 훅

**Claude Code 훅** (`.claude/hooks/` + `.claude/settings.json`)
- `tdd-guard.py` — `src/` 소스 파일 쓰기 전 테스트 파일 존재 확인. 없으면 차단
- `doc-sync-trigger.py` — 소스 파일 변경 후 갱신 필요한 docs/ 를 에이전트에게 알림

**Git 훅** (`hooks/`)
- `pre-commit` — 커밋 직전 lint→test→build 자동 실행 (언어 자동 감지)
- `pre-commit-review` — sub-agent가 diff만 보고 보안·성능·컨벤션 위반 탐지 (BLOCK/WARN)

### 문서 구조 (`docs/`)
| 디렉토리 | 용도 |
|---|---|
| `architecture/` | 시스템 구조, 레이어, 컴포넌트 관계 |
| `database/` | 스키마, 마이그레이션 이력, ERD |
| `design/` | UI/UX 명세, 화면 설계 |
| `tacit/` | 암묵지, 운영 노하우, 삽질 기록 |
| `api/` | 엔드포인트 명세, 요청/응답 스키마 |
| `adr/` | Architecture Decision Records |
| `history/` | 날짜별 변경 이력 |

## 시작하기

### 1. 이 레포를 복사한다

```bash
git clone https://github.com/binaryarc/ai-native-dev-starter.git
# 또는 내 프로젝트에 .claude/, hooks/, docs/, MAP.md, CLAUDE.md 복사
```

### 2. Git 훅을 설치한다

```bash
bash hooks/install-hooks.sh
```

### 3. MAP.md를 프로젝트에 맞게 수정한다

`MAP.md`의 `src/`, `docs/` 섹션을 실제 프로젝트 구조로 업데이트한다.

### 4. 에이전트와 함께 개발한다

```
/loop-work 새 기능 구현
/tdd 이메일 유효성 검사
/debate 모놀리식 vs 마이크로서비스 전환 여부
/nav 특정 파일 위치
/ai-ready-score
```

## 지원 언어 스택

Python · FastAPI · Java/Maven · Java/Gradle · Spring Boot ·
React · Node.js · Go · Rust · Kotlin · Docker Compose · Docker · Make

## Core Idea

AI 네이티브 개발은 "AI에게 코드를 맡기는 것"이 아니라,
사람이 **문제 정의와 검증 기준**을 설계하고
에이전트가 **반복 작업과 탐색**을 빠르게 수행하도록 만드는 개발 방식입니다.

이 스타터팩은 에이전트가 컨텍스트를 잃지 않고, 규칙을 지키며,
문서를 최신 상태로 유지하면서 일관되게 동작할 수 있는 **구조**를 제공합니다.

