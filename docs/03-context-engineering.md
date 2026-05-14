# Context Engineering

컨텍스트 엔지니어링은 에이전트가 문제를 올바르게 이해하도록 필요한 정보만 설계해서 제공하는 일입니다.

## Context Pack

작업 요청에 포함하면 좋은 정보입니다.

```text
Repository:
Goal:
Current behavior:
Expected behavior:
Relevant files:
Commands to run:
Constraints:
Definition of done:
```

## File Pointers

가능하면 파일명을 직접 제공합니다.

```text
관련 파일은 src/auth/session.ts, src/auth/session.test.ts 입니다.
```

파일을 모르면 에이전트에게 탐색을 맡깁니다.

```text
로그인 세션 처리 위치를 찾아서 관련 파일을 먼저 요약해줘.
```

## Logs

로그는 줄이지 말고, 관련 명령과 함께 제공합니다.

```text
명령:
npm test -- auth

실패 로그:
...
```

## Constraints

제약은 품질을 올립니다.

예시:

- public API는 바꾸지 말 것
- DB 마이그레이션은 추가하지 말 것
- 기존 컴포넌트 라이브러리만 사용할 것
- 테스트 없는 리팩터링은 하지 말 것

## Done Criteria

완료 기준이 없으면 에이전트는 "그럴듯한 중간 상태"에서 멈추기 쉽습니다.

좋은 완료 기준:

- 지정된 테스트 통과
- 재현 시나리오 해결
- 문서 업데이트
- PR 설명 초안 작성

