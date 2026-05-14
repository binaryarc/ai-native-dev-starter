---
name: skills-index
description: >
  이 프로젝트에서 사용 가능한 모든 스킬 목록과 빠른 시작 가이드.
  debate, loop-work, ai-ready-score, tdd, frontmatter 스킬 포함.
  어떤 스킬이 있는지 확인하거나 새 스킬을 등록할 때 참조.
type: index
load: on-demand
---

# SKILLS.md

이 디렉토리의 스킬은 모든 프로젝트, 모든 사용자가 공통으로 사용할 수 있습니다.
각 스킬 디렉토리 안의 `SKILL.md`에 상세 사용법이 있습니다.

## 등록된 스킬

| 스킬 | 호출 방법 | 설명 |
|---|---|---|
| [debate](./debate/SKILL.md) | `/debate <안건>` | Claude(전략가)와 Codex(분석가)가 헤드리스 CLI로 토론해 결론을 도출한다 |
| [loop-work](./loop-work/SKILL.md) | `/loop-work <작업 설명>` | 어떤 언어·프레임워크든 개발→빌드→테스트→검증→배포 루프를 완주한다 |
| [ai-ready-score](./ai-ready-score/SKILL.md) | `/ai-ready-score [경로]` | 코드베이스를 7카테고리 100점 루브릭으로 감사해 JSON + HTML 보고서를 산출한다 |
| [tdd](./tdd/SKILL.md) | `/tdd <기능 설명>` | Red→Green→Refactor 루프를 언어별 명령으로 실행한다 |
| [frontmatter](./frontmatter/SKILL.md) | `/frontmatter` | 마크다운 문서에 AI 에이전트 lazy-loading용 frontmatter를 작성한다 |
| [nav](./nav/SKILL.md) | `/nav <키워드>` | MAP.md를 진입점으로 2홉 이내에 파일·문서·심볼을 찾아 반환한다 |
| [doc-sync](./doc-sync/SKILL.md) | `/doc-sync [파일목록]` | 코드·파일 변경 후 docs/ 문서와 MAP.md를 자동으로 동기화한다 |

---

## debate

**Claude와 Codex가 토론해서 결론을 내린다.**

설계, 코드, 수치, 전략, 투자 등 어떤 안건이든 다각도로 검토가 필요할 때 사용한다.

### 빠른 시작

```bash
# PATH 확인 (codex가 nvm으로 설치된 경우)
export PATH="$HOME/.nvm/versions/node/v18.20.8/bin:$PATH"

# 스크립트 경로
DEBATE="$(find ~ -path "*/.claude/skills/debate/debate.py" 2>/dev/null | head -1)"

# 실행
python3 "$DEBATE" "여기에 안건을 입력하세요" --rounds 3
```

### Claude Code에서 사용

Claude Code 세션에서 아래와 같이 입력하면 자동으로 실행된다:

```
/debate <안건>
회의해줘: <안건>
토론시켜줘: <안건>
```

### 파라미터

| 파라미터 | 기본값 | 선택지 |
|---|---|---|
| `--rounds` | 3 | 2 (빠르게) ~ 5 (깊게) |
| `--claude-model` | sonnet | haiku, sonnet, opus |
| `--codex-model` | gpt-5.5 | gpt-5.4-mini, gpt-5.5 |
| `--quiet` | off | 결론만 출력할 때 |

### 사전 요건

- `claude` CLI 설치 및 인증 완료
- `codex` CLI 설치 (`npm install -g @openai/codex`) 및 `OPENAI_API_KEY` 설정

### 파일 구조

```
.claude/skills/debate/
├── SKILL.md      ← 상세 사용법 (Claude Code가 읽는 스킬 정의)
└── debate.py     ← 오케스트레이터 스크립트
```

---

## loop-work

**어떤 언어·프레임워크든 개발→테스트→검증→배포 루프를 완주한다.**

기능 구현, 버그 수정 등 코드 변경 후 검증까지 안전하게 완료하고 싶을 때 사용한다.

### Claude Code에서 사용

```
/loop-work <작업 설명>
테스트 후 반영해줘
검증하고 배포해줘
안전하게 배포해줘
```

### 지원 스택

| 스택 | 감지 파일 |
|---|---|
| Python | `pyproject.toml`, `requirements.txt` |
| FastAPI | `pyproject.toml` + fastapi import |
| Java / Maven | `pom.xml` |
| Java / Gradle | `build.gradle`, `build.gradle.kts` |
| Spring Boot | `@SpringBootApplication` + Maven/Gradle |
| React | `package.json` + react 의존성 |
| Node.js / JavaScript | `package.json` |
| Docker Compose | `docker-compose*.yml` |
| Docker (단일) | `Dockerfile` |
| Make 기반 | `Makefile` |

### 파일 구조

```
.claude/skills/loop-work/
├── SKILL.md          ← 스킬 정의 및 9단계 루프 절차
└── lang-profiles.md  ← 언어·프레임워크별 lint·테스트·빌드·배포 명령 상세
```
