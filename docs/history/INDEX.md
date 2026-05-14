---
name: docs-history
description: >
  날짜별 변경 이력. 기능 추가, 버그픽스, 설계 변경, 주요 결정을 날짜별로 기록.
  "이력", "변경", "히스토리", "언제", "YYYYMMDD" 키워드 시 로드.
type: index
load: on-demand
tags: [history, changelog, log]
updated: 2026-05-15
---

# History

날짜별 변경 이력을 기록한다. 파일명: `YYYYMMDD.md`

## 이력 목록

| 날짜 | 파일 | 주요 변경 |
|---|---|---|
| — | — | 아직 이력 없음 |

## 작성 가이드

- 코드 변경이 있는 작업이 끝날 때마다 `YYYYMMDD.md` 생성 또는 갱신
- 형식: `## HH:MM — <변경 요약>` + 상세 내용
- AI 에이전트가 작성 시 날짜는 오늘, 시간은 현재 시각 기준
