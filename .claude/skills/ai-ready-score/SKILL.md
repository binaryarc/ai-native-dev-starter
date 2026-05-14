---
name: ai-ready-score
description: >
  임의의 git 리포지토리를 AI-Ready 루브릭(100점, 7카테고리)으로 감사한다.
  JSON 점수표 + 한국어 HTML 대시보드 + ROI 우선순위 액션 리스트를 산출한다.
  Use when the user says "AI 준비도 점수 매겨줘", "ai-ready 감사해줘", "코드베이스 AI 준비 점수",
  "/ai-ready-score", "이 프로젝트 AI 준비됐어?", "AI 점수 보여줘", "score this repo".
argument-hint: "[리포지토리 경로 (생략 시 현재 디렉토리)]"
type: skill
load: on-demand
tags: [audit, score, ai-ready, rubric]
---

# AI-Ready Score 스킬

임의의 git 리포지토리를 **7카테고리 100점 루브릭**으로 자동 감사한다.

## 산출물

| 파일 | 설명 |
|---|---|
| `ai-ready-score.json` | 체크별 pass/fail + 점수 + 상세 메시지 |
| `ai-ready-score.html` | 한국어 시각화 대시보드 (브라우저에서 열기) |
| 콘솔 요약 | 등급·점수·상위 3개 액션 즉시 출력 |

## 루브릭 7카테고리

| ID | 카테고리 | 배점 |
|---|---|---|
| C1 | 컨텍스트 및 문서화 | 20점 |
| C2 | 코드 구조 및 모듈화 | 15점 |
| C3 | 테스트 커버리지 및 품질 | 15점 |
| C4 | AI 툴링 설정 | 15점 |
| C5 | 의존성 및 환경 관리 | 10점 |
| C6 | Git 위생 | 15점 |
| C7 | 보안 및 시크릿 안전성 | 10점 |

## 등급 기준

| 등급 | 점수 | 의미 |
|---|---|---|
| S | 90+ | AI-Native: 즉시 AI 에이전트 투입 가능 |
| A | 80+ | AI-Ready: 경미한 개선 후 사용 가능 |
| B | 65+ | AI-Friendly: 중간 수준 준비됨 |
| C | 50+ | AI-Assisted: 기초 준비 필요 |
| D | 35+ | AI-Aware: 상당한 개선 필요 |
| F | 0+ | AI-Unready: 전면 재구성 필요 |

## 실행 방법

### Claude Code에서 사용

```
/ai-ready-score
/ai-ready-score /path/to/repo
이 프로젝트 AI 준비도 점수 매겨줘
```

Claude Code가 아래 명령을 자동 실행한다:

```bash
SCORER="$(find ~ -path "*/.claude/skills/ai-ready-score/scorer.py" 2>/dev/null | head -1)"
python3 "$SCORER" [리포지토리 경로]
```

### 직접 실행

```bash
# 현재 디렉토리 감사
python3 ~/.claude/skills/ai-ready-score/scorer.py

# 특정 리포지토리 감사
python3 ~/.claude/skills/ai-ready-score/scorer.py /path/to/repo

# JSON만 출력 (HTML 생략)
python3 ~/.claude/skills/ai-ready-score/scorer.py . --json-only

# 출력 경로 지정
python3 ~/.claude/skills/ai-ready-score/scorer.py . \
  --out-json ./reports/score.json \
  --out-html ./reports/score.html

# 커스텀 루브릭 사용
python3 ~/.claude/skills/ai-ready-score/scorer.py . --rubric ./my-rubric.json
```

## 결과 해석 및 후속 액션

1. **HTML 파일을 브라우저에서 열어** 카테고리별 점수와 ROI 액션 리스트 확인
2. `ai-ready-score.json`의 `actions` 배열을 파싱해 CI/이슈 트래커에 자동 등록 가능
3. 우선순위 `critical` → `high` → `medium` → `low` 순으로 액션 처리
4. 각 액션의 `points_gain` 대비 `effort_minutes`로 ROI 판단

## 루브릭 커스터마이징

`rubric.json`을 복사해 프로젝트 전용 루브릭을 만들 수 있다:

```bash
cp ~/.claude/skills/ai-ready-score/rubric.json ./my-rubric.json
# 점수·체크 조건 수정 후
python3 ~/.claude/skills/ai-ready-score/scorer.py . --rubric ./my-rubric.json
```

## 파일 구조

```
.claude/skills/ai-ready-score/
├── SKILL.md      ← 이 파일 (Claude Code 스킬 정의)
├── rubric.json   ← 7카테고리 100점 루브릭 정의
└── scorer.py     ← 감사 실행 스크립트
```

## 주의사항

- Python 3.10+ 필요 (표준 라이브러리만 사용, 추가 설치 불필요)
- git 명령이 필요한 체크(C6)는 git이 설치된 환경에서만 동작
- C7-2 시크릿 탐지는 false positive 가능 — 결과를 수동으로 확인할 것
- `.git/` 디렉토리가 없는 경우 git 관련 체크는 자동으로 0점 처리
