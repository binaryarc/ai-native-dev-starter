---
name: frontmatter
description: >
  .claude/ 하위 또는 프로젝트의 모든 마크다운 문서에 AI 에이전트 lazy-loading용 frontmatter를 작성한다.
  Use when the user says "frontmatter 붙여줘", "md 파일에 frontmatter 추가", "/frontmatter",
  "lazy loading 설정해줘", "새 md 파일 만들어줘", or when creating any new markdown document.
argument-hint: "[대상 파일 또는 디렉토리 (생략 시 현재 디렉토리 전체)]"
---

# frontmatter 스킬

모든 마크다운 문서에 AI 에이전트가 **필요할 때만 로드(lazy-load)** 할 수 있도록
표준 frontmatter를 작성한다.

---

## Lazy Loading이란

AI 에이전트(Claude Code, Codex, Gemini 등)는 대화 시작 시 모든 파일을 컨텍스트에
올리지 않는다. frontmatter의 `description`을 읽고 **지금 필요한 파일인지 판단**한 뒤
필요한 경우에만 내용을 로드한다.

`description`이 없거나 모호하면 에이전트는 파일을 로드할지 판단할 수 없어
무시하거나 불필요하게 전부 로드한다.

---

## Frontmatter 표준 스펙

```yaml
---
name: <kebab-case 식별자>
description: >
  한 줄~세 줄. 에이전트가 "이 파일이 지금 필요한가?"를 판단하는 핵심 텍스트.
  언제(when), 무엇을(what) 담고 있는지를 구체적으로 서술한다.
  트리거 키워드를 포함하면 에이전트가 더 정확히 매칭한다.
type: <타입>          # 아래 타입 목록 참조
tags: [태그1, 태그2]  # 선택. 검색·필터링용
load: <로드 정책>     # always | on-demand | never
---
```

### type 목록

| type | 용도 |
|---|---|
| `skill` | 에이전트가 호출하는 실행 가능한 절차 (`/skill-name`) |
| `rule` | 항상 적용되는 행동 원칙 |
| `reference` | 언어·프레임워크별 명령, API 레퍼런스 |
| `context` | 프로젝트 전체 컨텍스트 (CLAUDE.md 등) |
| `index` | 다른 문서의 목록·인덱스 |
| `template` | 재사용 가능한 템플릿 |
| `checklist` | 단계별 체크리스트 |
| `adr` | Architecture Decision Record |

### load 정책

| load | 의미 |
|---|---|
| `always` | 에이전트 시작 시 항상 로드 (CLAUDE.md, 핵심 rule) |
| `on-demand` | description 매칭 시에만 로드 (대부분의 문서) |
| `never` | 에이전트가 로드하지 않음 (사람 전용 문서) |

---

## 파일 유형별 작성 예시

### CLAUDE.md / AGENTS.md / GEMINI.md (context)

```yaml
---
name: claude-context
description: >
  이 프로젝트의 AI 에이전트 행동 지침. 코딩 원칙, 컨텍스트 파일 길이 제한,
  TDD 정책 등 모든 작업에 적용되는 기본 규칙을 담고 있다.
type: context
load: always
---
```

### rule 파일

```yaml
---
name: tdd
description: >
  TDD 원칙 — 모든 코드 변경은 테스트를 먼저 작성한다.
  구현 전 Red-Green-Refactor 루프 규칙. 언어별 명령은 skills/tdd/SKILL.md 참조.
type: rule
load: always
---
```

### skill 파일

```yaml
---
name: loop-work
description: >
  개발→빌드→테스트→검증→배포 루프 실행 절차.
  "테스트 후 반영", "검증하고 배포" 등 안전한 배포가 필요할 때 사용.
  언어별 명령은 lang-profiles.md 참조.
type: skill
load: on-demand
---
```

### reference 파일 (lang-profiles.md 등)

```yaml
---
name: lang-profiles
description: >
  Python, FastAPI, Java/Maven, Gradle, Spring Boot, React, Node.js,
  Docker Compose, Docker, Make 의 lint·테스트·빌드·배포 명령 레퍼런스.
  loop-work 또는 tdd 스킬 실행 시 언어별 명령이 필요할 때 로드.
type: reference
load: on-demand
tags: [python, java, spring, react, docker, gradle, maven]
---
```

### index 파일 (SKILLS.md 등)

```yaml
---
name: skills-index
description: >
  사용 가능한 모든 스킬 목록. debate, loop-work, ai-ready-score, tdd, frontmatter.
  어떤 스킬이 있는지 확인하거나 새 스킬을 등록할 때 참조.
type: index
load: on-demand
---
```

### README.md

```yaml
---
name: project-readme
description: >
  프로젝트 개요, 목적, 디렉토리 구조, 시작 방법.
  이 리포지토리가 무엇인지, 어떻게 쓰는지 파악할 때 참조.
type: context
load: on-demand
---
```

---

## 작성 원칙

**description은 에이전트의 검색 쿼리다.**

- 나쁨: `"루프 스킬"` — 너무 짧고 모호
- 좋음: `"개발→빌드→테스트→검증→배포 루프. '테스트 후 반영', '검증하고 배포' 요청 시 사용"` — 트리거 상황 포함

**load 정책 판단 기준:**
- `always`: 매 작업에 영향을 주는 원칙·규칙 (5개 이하 유지)
- `on-demand`: 특정 작업에만 필요한 문서 (대부분)
- `never`: 온보딩 가이드, 외부 공유용 등 에이전트 불필요

**기존 파일 수정 시:**
- 파일 맨 위에 `---`로 감싼 frontmatter 블록 추가
- 기존 `# 제목` 헤더는 그대로 유지 (frontmatter 아래에 위치)

---

## 체크리스트

새 마크다운 파일 생성 시:
- [ ] `name`: kebab-case, 파일명과 일치 또는 유사
- [ ] `description`: 에이전트가 "지금 필요한가?" 판단 가능한 내용
- [ ] `type`: 위 목록 중 하나
- [ ] `load`: always / on-demand / never 중 선택
- [ ] `tags`: 언어·도메인 키워드 (reference 타입은 필수)
