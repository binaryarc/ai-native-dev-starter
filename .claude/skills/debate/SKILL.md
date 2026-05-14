---
name: debate
description: >
  Claude(전략가)와 Codex(분석가)를 헤드리스 CLI로 실행해 안건에 대해 다각도로 토론하고 결론을 도출한다.
  설계·코드·수치·전략·투자 결정 등 어떤 안건이든 사용 가능.
  "회의해줘", "토론시켜줘", "ai-debate 해줘", "/debate <안건>" 형식으로 호출.
type: skill
load: on-demand
tags: [debate, decision, design, architecture]
---

## 목적

이 스킬 디렉토리의 `debate.py`를 실행해 Claude와 Codex가 주어진 안건을 두고 헤드리스 CLI로 토론하게 한다.
- Claude(`claude -p`)는 전략가 역할 — 창의적·비판적 시각으로 논증
- Codex(`codex exec --ephemeral`)는 분석가 역할 — 데이터·실현 가능성 중심으로 논증
- 마지막 라운드 후 Claude가 사회자로서 합의 결론과 실행 권고안을 정리

## 실행 방법

사용자가 `/debate <안건>` 또는 "회의해줘", "토론시켜줘", "ai-debate 해줘" 등을 입력하면 아래를 수행한다.

### 1단계: 안건 파악

사용자 입력에서 안건을 추출한다. 안건이 불분명하면 한 문장으로 정리해서 확인 후 진행한다.

### 2단계: 최신 데이터 수집 (안건이 시장/투자/뉴스 관련일 때)

안건이 투자·시장·경제·뉴스 관련이면 `claude -p --allowedTools "WebSearch,WebFetch"`로 관련 최신 데이터를 먼저 수집한 뒤 안건 프롬프트에 포함시킨다.

일반 전략/기술/설계 안건은 이 단계를 건너뛴다.

### 3단계: debate.py 실행

```bash
export PATH="$HOME/.nvm/versions/node/v18.20.8/bin:$PATH"
SKILL_DIR="$(find ~/.claude /home/*/ai-native-dev-starter/.claude -name "debate.py" 2>/dev/null | head -1 | xargs dirname)"
python3 "$SKILL_DIR/debate.py" "<안건 전체 텍스트>" --rounds <N> --claude-model sonnet --codex-model gpt-5.5
```

라운드 수 기본값: 3. 사용자가 "빠르게", "간단히"라고 하면 2, "깊게", "철저히"라고 하면 4~5.

### 4단계: 결과 요약

회의가 끝나면 최종 결론 섹션을 마크다운 표로 정리해서 사용자에게 보여준다.

## 옵션

| 옵션 | 설명 | 예시 |
|---|---|---|
| `--rounds N` | 토론 라운드 수 (기본 3) | `--rounds 2` |
| `--claude-model` | Claude 모델 (기본 sonnet) | `--claude-model opus` |
| `--codex-model` | Codex 모델 (기본 gpt-5.5) | `--codex-model gpt-5.4-mini` |
| `--quiet` | 중간 발언 숨기고 결론만 출력 | `--quiet` |

## 회의가 필요한 상황

아래 상황에서 자동으로 회의를 제안하거나 사용자가 요청하면 즉시 실행한다.

- **설계 결정**: 아키텍처 변경, 레이어 경계 재정의, 새 모듈 도입
- **코드 결정**: 핵심 로직 전략, 리스크 관리 방식, 외부 서비스 연동 방식
- **수치 결정**: ML 하이퍼파라미터, 임계값, 타임아웃 등 설정값
- **트레이드오프**: 두 가지 이상의 접근법 중 어느 쪽이 나은지 불명확할 때
- **투자/시장 분석**: 종목·섹터·타이밍 판단 (5개 게이트 프레임워크 자동 적용)

## 주의사항

- 실행 전 `which codex`로 PATH 확인. 없으면 `export PATH="$HOME/.nvm/versions/node/v18.20.8/bin:$PATH"` 선행.
- 라운드당 약 30~60초 소요. 3라운드 기준 총 3~5분.
- 안건 텍스트에 쌍따옴표가 포함되면 이스케이프 처리 또는 heredoc으로 전달.
- `cwd="/tmp"` 고정으로 실행 — Claude subprocess가 현재 디렉토리의 CLAUDE.md를 읽다가 무한 대기하는 버그 방지.

## 사용 예시

```
/debate 주 4일 근무제를 도입해야 하는가
/debate 지금 SK하이닉스를 사야 하는가 --rounds 2
/debate 우리 서비스의 모놀리식 vs 마이크로서비스 전환 여부
/debate GraphQL vs REST API 선택 기준
/debate stop_loss_pct를 5%로 설정하는 게 적절한가
```
