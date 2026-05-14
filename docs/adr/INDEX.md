---
name: docs-adr
description: >
  Architecture Decision Records. 기술·설계 결정의 맥락, 선택지, 결과를 기록.
  "ADR", "결정", "왜", "선택", "트레이드오프" 키워드 시 로드.
type: index
load: on-demand
tags: [adr, decision, architecture, tradeoff]
updated: 2026-05-15
---

# ADR (Architecture Decision Records)

중요한 기술·설계 결정을 번호 순으로 기록한다.
한번 기록된 ADR은 수정하지 않고 새 ADR로 supersede한다.

## 결정 목록

| ADR | 제목 | 상태 | 날짜 |
|---|---|---|---|
| — | — | — | — |

## 상태 값

`proposed` · `accepted` · `deprecated` · `superseded by ADR-NNN`

## 파일명 규칙

`ADR-NNN-<짧은-제목>.md` (예: `ADR-001-use-postgresql.md`)

## 템플릿

```markdown
# ADR-NNN: 제목

## 상태
accepted

## 맥락
왜 이 결정이 필요했는가.

## 결정
무엇을 선택했는가.

## 선택지
- 옵션 A: ...
- 옵션 B: ...

## 결과
이 결정으로 얻는 것과 잃는 것.
```
