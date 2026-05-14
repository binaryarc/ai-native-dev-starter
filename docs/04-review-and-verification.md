# Review And Verification

AI가 만든 코드는 빠르게 나오지만, 검증 없이 신뢰하면 안 됩니다.

## Review Order

1. 요구사항을 실제로 만족하는지 확인합니다.
2. 변경 범위가 과도하지 않은지 확인합니다.
3. 테스트가 의미 있는 실패를 잡는지 확인합니다.
4. 엣지 케이스와 에러 처리를 확인합니다.
5. 배포 리스크를 확인합니다.

## Ask The Agent For A Review

```text
코드 리뷰 관점으로 diff를 점검해줘. 버그, 회귀 가능성, 누락된 테스트를 우선순위로 지적하고, 스타일 취향은 제외해줘.
```

## Verification Matrix

| Area | Question |
| --- | --- |
| Behavior | 사용자가 보는 동작이 바뀌었나? |
| Contract | API, 타입, DB 스키마 계약이 바뀌었나? |
| State | 캐시, 세션, 동시성 문제가 생길 수 있나? |
| Failure | 실패 경로가 테스트되었나? |
| Observability | 문제가 생겼을 때 확인할 로그가 있나? |

## Red Flags

- 관련 없는 대규모 리팩터링
- 테스트 삭제
- 타입 오류 무시
- 임시 fallback이 영구 코드처럼 들어감
- 실패 로그를 확인하지 않은 추측성 수정

