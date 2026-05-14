---
name: tdd
description: >
  Red→Green→Refactor 루프를 언어별 명령으로 실행한다.
  Use when the user says "TDD로 만들어줘", "테스트 먼저 작성해줘", "/tdd",
  "Red-Green-Refactor", "테스트 주도로 개발해줘".
argument-hint: "<구현할 기능 또는 수정할 버그>"
type: skill
load: on-demand
tags: [python, java, spring, react, nodejs, docker, tdd, test]
---

# TDD 스킬

**Red → Green → Refactor** 순서를 언어별 명령으로 실행한다.

---

## 루프 절차

### Red — 실패하는 테스트 작성

구현 전에 테스트를 먼저 작성한다.

- 테스트 이름은 "무엇을 기대하는지"를 서술한다.
  - 좋음: `test_returns_empty_list_when_no_items()`
  - 나쁨: `test_function()`
- 하나의 동작만 검증한다. 테스트 하나에 assert 하나를 기본으로.
- 테스트를 실행해 **실제로 실패**하는 것을 확인한다.

```
§ 언어별 테스트 실행 명령 참조
```

실패 메시지가 "구현이 없어서 실패"인지 확인. 다른 이유로 실패하면 테스트 자체를 수정.

---

### Green — 최소 구현

테스트를 통과하는 **가장 단순한 코드**만 작성한다.

- 이 단계에서 설계를 완벽하게 하려 하지 않는다.
- 하드코딩도 허용 — 일단 Green을 만드는 것이 목표.
- 테스트를 실행해 **통과**하는 것을 확인한다.

---

### Refactor — 정리

동작을 유지하며 코드 품질을 높인다.

- 중복 제거, 네이밍 개선, 추상화 도입.
- 매 변경 후 테스트를 실행해 Green 유지를 확인.
- 테스트 코드도 리팩토링 대상이다.

---

## § 언어별 명령

### Python / FastAPI

```bash
# Red: 테스트 실행 (실패 확인)
uv run pytest tests/test_<module>.py::test_<name> -v
# 또는
pytest tests/test_<module>.py::test_<name> -v

# Green: 구현 후 재실행
uv run pytest tests/test_<module>.py -x -v

# Refactor: 전체 suite 통과 확인
uv run pytest -x -m "not slow and not integration"

# 커버리지 확인
uv run pytest --cov=src --cov-report=term-missing
```

**파일 위치 규칙:**
- 소스: `src/<package>/<module>.py`
- 테스트: `tests/test_<module>.py`
- 함수 단위: `test_<함수명>_<시나리오>()`

---

### Java / Maven

```bash
# Red: 특정 테스트 실행 (실패 확인)
mvn test -Dtest=<TestClass>#<testMethod> -pl <module>

# Green: 클래스 단위 재실행
mvn test -Dtest=<TestClass> -pl <module>

# Refactor: 전체 단위 테스트
mvn test -Dgroups="unit"

# 커버리지 (JaCoCo)
mvn verify -Dgroups="unit"
# target/site/jacoco/index.html 확인
```

**파일 위치 규칙:**
- 소스: `src/main/java/<package>/<Class>.java`
- 테스트: `src/test/java/<package>/<Class>Test.java`
- 메서드: `@Test void <동작>_<시나리오>()`

---

### Java / Gradle

```bash
# Red: 특정 테스트 실행
./gradlew test --tests "<package>.<TestClass>.<method>"

# Green: 클래스 단위
./gradlew test --tests "<package>.<TestClass>"

# Refactor: 전체
./gradlew test -PincludeTags="unit"

# 커버리지 (JaCoCo)
./gradlew jacocoTestReport
# build/reports/jacoco/test/html/index.html 확인
```

---

### Spring Boot

```bash
# Red: 슬라이스 테스트 (@WebMvcTest, @DataJpaTest)
./gradlew test --tests "*.<ControllerTest>.<method>"

# Green: 슬라이스 전체
./gradlew test --tests "*.<ControllerTest>"

# Refactor: 단위 테스트 전체 (통합 테스트 제외)
./gradlew test -PexcludeTags="integration"

# 통합 테스트 별도 확인
./gradlew integrationTest
```

**Spring 테스트 계층:**
- `@ExtendWith(MockitoExtension.class)` — 순수 단위 테스트 (빠름)
- `@WebMvcTest` — 컨트롤러 슬라이스
- `@DataJpaTest` — 리포지토리 슬라이스
- `@SpringBootTest` — 통합 테스트 (느림, Refactor 후에만)

---

### React / TypeScript

```bash
# Red: 특정 테스트 실행
npx vitest run src/<component>.test.tsx
# 또는
npm test -- --testPathPattern="<component>" --watchAll=false

# Green: 파일 단위
npx vitest run src/<component>.test.tsx

# Refactor: 전체
npx vitest run
# 또는
npm test -- --watchAll=false

# 커버리지
npx vitest run --coverage
```

**파일 위치 규칙:**
- 소스: `src/components/<Component>.tsx`
- 테스트: `src/components/<Component>.test.tsx`
- 훅: `src/hooks/<useHook>.test.ts`

**테스트 우선순위:** 로직(hooks, utils) → 컴포넌트 → 통합

---

### Node.js / JavaScript

```bash
# Red
npx jest <module>.test.js --verbose
# 또는
npx mocha tests/<module>.test.js

# Green
npx jest <module>.test.js

# Refactor
npx jest --coverage
```

---

### Docker Compose 포함 프로젝트

```bash
# 단위 테스트는 컨테이너 없이 먼저
uv run pytest -x -m "not integration"   # Python
./gradlew test -PexcludeTags="integration"  # Java

# Green 확인 후 통합 테스트
docker compose -f docker-compose.test.yml up -d
uv run pytest -x -m "integration"
docker compose -f docker-compose.test.yml down --volumes
```

---

## 체크리스트

Red 단계 전:
- [ ] 테스트 이름이 기대 동작을 서술하는가?
- [ ] 기존 테스트와 중복되지 않는가?
- [ ] 하나의 동작만 검증하는가?

Green 단계 전:
- [ ] 테스트가 실제로 실패하는 것을 확인했는가?
- [ ] 실패 이유가 "구현 없음"인가?

Refactor 단계 전:
- [ ] 모든 테스트가 Green인가?
- [ ] 리팩토링 후 매번 테스트를 재실행하는가?

커밋 시:
- `hooks/pre-commit`이 lint·test·build를 자동 실행한다. 별도 수동 실행 불필요.

---

## 사용 예시

```
/tdd 사용자 이메일 유효성 검사 함수
/tdd 재고 부족 시 주문 실패 처리
/tdd GET /api/users/:id 엔드포인트
```
