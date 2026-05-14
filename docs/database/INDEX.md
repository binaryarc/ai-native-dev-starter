---
name: docs-database
description: >
  데이터베이스 스키마, 마이그레이션 이력, ERD, 인덱스 전략 문서.
  "DB", "스키마", "테이블", "마이그레이션", "ERD", "인덱스" 키워드 시 로드.
type: index
load: on-demand
tags: [database, schema, migration, erd, sql]
updated: 2026-05-15
---

# Database

DB 스키마와 마이그레이션 이력을 기록한다.

## 파일 목록

| 파일 | 테이블/컬렉션 | 설명 |
|---|---|---|
| — | — | 아직 문서 없음 |

## 작성 가이드

- `schema.md` — 현재 스키마 스냅샷 (테이블·컬럼·타입·제약)
- `migrations/` — 마이그레이션 파일별 변경 요약
- ERD는 Mermaid `erDiagram` 블록으로 작성
- 스키마 변경 시 반드시 이 INDEX.md 갱신
