---
name: doc-sync
description: >
  코드·파일 추가·삭제·변경 후 docs/ 의 알맞은 문서를 자동으로 갱신한다.
  MAP.md 소스 코드 인덱스, 각 docs/ 하위 INDEX.md, history/ 이력을 동기화.
  "문서 업데이트", "docs 갱신", "MAP 업데이트", "/doc-sync" 호출 시 사용.
  코드 변경이 있는 모든 작업 완료 후 자동 실행 권장.
argument-hint: "[변경된 파일 목록 (생략 시 git diff 기준 자동 감지)]"
type: skill
load: on-demand
tags: [docs, sync, map, index, history]
---

# doc-sync 스킬

코드·파일 변경 후 **docs/ 문서를 자동으로 동기화**한다.
변경 유형을 감지해 알맞은 문서만 선택적으로 갱신한다.

---

## 실행 시점

아래 중 하나라도 해당하면 `/doc-sync` 를 실행한다:

| 변경 유형 | 갱신 대상 |
|---|---|
| `src/` 파일 추가·삭제·이름변경 | MAP.md 소스 코드 인덱스 |
| `src/` 파일 주요 함수·클래스 추가·삭제 | MAP.md 소스 코드 인덱스 |
| DB 스키마·마이그레이션 변경 | `docs/database/INDEX.md` + 해당 스키마 문서 |
| API 엔드포인트 추가·변경·삭제 | `docs/api/INDEX.md` + 해당 API 문서 |
| 아키텍처·레이어 구조 변경 | `docs/architecture/INDEX.md` |
| 중요 설계 결정 | `docs/adr/` 새 ADR 파일 |
| UI 컴포넌트·화면 추가·변경 | `docs/design/INDEX.md` |
| 코드에 드러나지 않는 운영 지식 발견 | `docs/tacit/INDEX.md` + 해당 문서 |
| 코드 변경이 있는 모든 작업 완료 | `docs/history/YYYYMMDD.md` 이력 추가 |

---

## 실행 절차

### 1단계: 변경 파일 수집

인자가 있으면 그 목록을 사용. 없으면 git으로 자동 감지:

```bash
git diff --name-only HEAD        # 커밋된 변경
git diff --name-only             # 미커밋 변경
git diff --name-only --staged    # 스테이징된 변경
```

### 2단계: 변경 유형 분류

수집된 파일 목록을 아래 규칙으로 분류한다:

```
src/**          → [src-change]   MAP.md 소스 코드 인덱스 갱신
*migration*     → [db-change]    docs/database/ 갱신
*schema*        → [db-change]
*router*|*api*|*endpoint*|*controller* → [api-change]  docs/api/ 갱신
*component*|*page*|*screen*|*view*     → [design-change] docs/design/ 갱신
```

### 3단계: 문서별 갱신

#### MAP.md — 소스 코드 인덱스 (`[src-change]`)

1. 변경된 `src/` 파일을 Read한다
2. 최상위 public 함수·클래스·상수를 추출한다
3. MAP.md 의 `## 소스 코드 인덱스` 표를 갱신한다:
   - 추가된 파일 → 행 추가
   - 삭제된 파일 → 행 제거
   - 심볼 변경 → 해당 행 수정

```markdown
| 파일 | 심볼 | 설명 |
|---|---|---|
| src/api/user.py | `UserService`, `get_user`, `create_user` | 사용자 CRUD 서비스 |
```

#### docs/database/INDEX.md (`[db-change]`)

1. 변경된 스키마·마이그레이션 파일을 Read한다
2. `docs/database/INDEX.md` 의 파일 목록 표를 갱신한다
3. 새 테이블·컬럼이 있으면 `docs/database/schema.md` 에 반영한다
4. 마이그레이션이면 `docs/database/migrations/` 에 요약 파일 추가한다

#### docs/api/INDEX.md (`[api-change]`)

1. 변경된 라우터·컨트롤러 파일을 Read한다
2. 추가·변경·삭제된 엔드포인트를 파악한다
3. `docs/api/INDEX.md` 의 파일 목록 표를 갱신한다
4. 해당 엔드포인트 그룹 md 파일이 없으면 새로 생성한다:
   - frontmatter 포함 (`/frontmatter` 스킬 규칙 적용)
   - 메서드·경로·파라미터·응답 예시 포함

#### docs/design/INDEX.md (`[design-change]`)

1. 변경된 컴포넌트·페이지 파일을 Read한다
2. `docs/design/INDEX.md` 의 파일 목록 표를 갱신한다
3. 신규 컴포넌트면 `docs/design/<component-name>.md` 를 생성한다

#### docs/adr/ (중요 설계 결정 시)

다음 중 하나라도 해당하면 새 ADR을 생성한다:
- 라이브러리·프레임워크 교체
- DB 엔진·ORM 변경
- API 구조 전면 변경
- 인증 방식 변경

파일명: `ADR-NNN-<짧은-제목>.md`
번호: `docs/adr/INDEX.md` 의 마지막 번호 + 1

#### docs/history/YYYYMMDD.md (모든 코드 변경)

오늘 날짜 파일에 이력을 추가한다. 파일이 없으면 생성:

```markdown
---
name: history-YYYYMMDD
description: YYYY-MM-DD 변경 이력
type: reference
load: on-demand
---

# YYYY-MM-DD

## HH:MM — <변경 요약 한 줄>

- 변경 파일: `src/...`
- 내용: 무엇을 왜 변경했는가
- 영향: 어떤 동작이 달라지는가
```

`docs/history/INDEX.md` 의 이력 목록 표에도 행을 추가한다.

### 4단계: MAP.md updated: 갱신

```markdown
updated: YYYY-MM-DD   ← 오늘 날짜로 교체
```

---

## 새 문서 생성 규칙

모든 새 문서는 frontmatter를 포함해야 한다 → `/frontmatter` 스킬 참조.

최소 필수 필드:
```yaml
---
name: <kebab-case>
description: >
  한 줄 설명 — 에이전트가 "지금 필요한가?" 판단 가능한 내용
type: <skill|rule|reference|context|index|adr>
load: on-demand
updated: YYYY-MM-DD
---
```

---

## docs/ 디렉토리 구조

```
docs/
├── architecture/   ← 시스템 구조, 레이어, 컴포넌트 관계
│   └── INDEX.md
├── database/       ← 스키마, 마이그레이션 이력, ERD
│   └── INDEX.md
├── design/         ← UI/UX 명세, 화면 설계, 컴포넌트 가이드
│   └── INDEX.md
├── tacit/          ← 암묵지, 운영 노하우, 삽질 기록
│   └── INDEX.md
├── api/            ← 엔드포인트 명세, 요청/응답 스키마
│   └── INDEX.md
├── adr/            ← Architecture Decision Records
│   └── INDEX.md
└── history/        ← 날짜별 변경 이력 (YYYYMMDD.md)
    └── INDEX.md
```

각 디렉토리의 `INDEX.md` 가 해당 영역의 홉 2 진입점이다.

---

## 사용 예시

```
/doc-sync
/doc-sync src/api/user.py src/models/user.py
코드 변경했으니 문서 업데이트해줘
docs 갱신해줘
```
