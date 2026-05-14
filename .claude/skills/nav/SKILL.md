---
name: nav
description: >
  MAP.md를 진입점으로 2홉 이내에 파일·심볼·문서를 찾아 바로 링크를 반환한다.
  grep·find 없이 키워드만으로 파일 위치를 안내한다.
  "어디 있어?", "파일 찾아줘", "~가 뭐야?", "어느 파일에 있어?", "/nav <키워드>" 호출 시 사용.
argument-hint: "<찾을 키워드 또는 파일명>"
type: skill
load: on-demand
tags: [navigation, search, map, index]
---

# nav 스킬

**MAP.md → 목적지** 2홉 네비게이션.
grep·find 없이 키워드로 파일 위치를 즉시 안내한다.

---

## 동작 방식

```
홉 1: MAP.md 를 읽는다
홉 2: MAP.md 의 링크를 따라 목적지 파일을 읽는다
```

MAP.md 한 번 읽으면 프로젝트 전체 구조가 보인다.
링크를 한 번 더 따라가면 목적지다.
그 이상 탐색은 필요 없다.

---

## 실행 절차

### 1단계: MAP.md 읽기

```
Read MAP.md
```

MAP.md의 인덱스 테이블과 섹션을 훑어 키워드와 매칭되는 항목을 찾는다.

### 2단계: 매칭 판단

| 키워드 유형 | MAP.md 에서 찾을 위치 |
|---|---|
| 스킬 이름 (`debate`, `tdd` 등) | skills/ 표 |
| 규칙·원칙 | rules/ 표 |
| 함수·클래스명 | 소스 코드 인덱스 |
| 문서 주제 | 문서 인덱스 |
| 설정 파일 | 설정 파일 표 |
| 구조·디렉토리 | docs/, src/, templates/ 섹션 |

### 3단계: 결과 반환

**매칭됨** → 파일 경로 + 링크를 바로 반환한다. 파일을 열 필요가 있으면 Read한다.

**매칭 안 됨** → MAP.md 에 없다는 것을 알리고, 다음 중 하나를 제안한다:
- MAP.md 업데이트가 필요한 새 파일
- 오타 또는 다른 키워드로 재시도

**MAP.md 자체가 없을 때** → 사용자에게 MAP.md 생성을 안내한다:
```
MAP.md 가 없습니다. /frontmatter 스킬로 생성하거나
ai-native-dev-starter 의 MAP.md 를 복사해 사용하세요.
```

---

## 응답 형식

```
📍 <키워드> → <파일 경로>

파일: <상대 경로>
설명: <MAP.md 의 설명 한 줄>
링크: <마크다운 링크>

[필요 시] 관련 파일:
- <연관 파일 1>
- <연관 파일 2>
```

---

## MAP.md 업데이트 시점

nav 스킬 실행 중 키워드가 MAP.md 에 없고 실제 파일은 존재할 때:
→ MAP.md 의 해당 섹션에 행을 추가하고 `updated:` 날짜를 갱신한다.

---

## 사용 예시

```
/nav debate
/nav TDD 테스트
/nav lang-profiles
/nav scorer.py
/nav 루브릭
/nav 배포 명령
debate 스킬 어디 있어?
lang-profiles 찾아줘
```
