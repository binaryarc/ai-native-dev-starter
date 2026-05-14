---
name: lang-profiles
description: >
  Python, FastAPI, Java/Maven, Gradle, Spring Boot, React, Node.js,
  Go, Rust, Kotlin, Docker Compose, Docker, Make 의 lint·테스트·빌드·배포·정리 명령 레퍼런스.
  loop-work 또는 tdd 스킬 실행 시 언어별 명령이 필요할 때 로드.
type: reference
load: on-demand
tags: [python, fastapi, java, spring, maven, gradle, react, nodejs, go, rust, kotlin, docker, make]
---

# lang-profiles.md

loop-work 스킬의 언어·프레임워크별 명령 참조.
각 섹션은 독립적이며, 프로젝트에 해당하는 섹션만 적용한다.

---

## Python (순수 / FastAPI 공통 기반)

**감지**: `pyproject.toml` 또는 `requirements.txt` 존재

### Lint / Format

```bash
# uv 사용 시 (권장)
uv run ruff check src/ tests/ --fix
uv run ruff format src/ tests/

# pip 사용 시
ruff check src/ tests/ --fix
ruff format src/ tests/

# 타입 체크 (선택)
uv run mypy src/
```

### 단위 테스트

```bash
# uv
uv run pytest -x -m "not slow and not integration"

# pip
pytest -x -m "not slow and not integration"

# 특정 파일만
uv run pytest tests/test_<module>.py -x -v
```

### 빌드

Python은 별도 빌드 불필요. 의존성만 확인:

```bash
uv sync          # uv 사용 시
pip install -e . # pip 사용 시
```

### Smoke Test

```bash
python -c "import <main_module>; print('import ok')"
```

### 배포 (로컬 서버 재시작)

```bash
# systemd
sudo systemctl restart <service-name>

# 직접 실행
pkill -f "python.*<app>" && nohup python -m <module> &
```

### 정리

```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

---

## FastAPI

**감지**: `pyproject.toml` + `fastapi` import 또는 `requirements.txt`에 `fastapi`

> Python 기반 공통 명령(lint·테스트) + 아래 FastAPI 전용 명령을 함께 사용한다.

### 개발 서버 기동

```bash
# uv
uv run uvicorn <module>:app --reload --port 8000

# pip
uvicorn <module>:app --reload --port 8000

# Docker가 있으면 Docker 섹션 우선 사용
```

### Smoke Test

```bash
curl -sf http://localhost:8000/health
curl -sf http://localhost:8000/docs   # Swagger UI 확인
```

### 통합 테스트

```bash
# pytest + httpx (TestClient)
uv run pytest tests/test_api/ -x -m "not slow"

# 특정 엔드포인트 수동 확인
curl -sf http://localhost:8000/api/<endpoint> | python3 -m json.tool
```

### 마이그레이션 (Alembic 사용 시)

```bash
# 테스트 DB에서 먼저 확인
DATABASE_URL=<test-db-url> uv run alembic upgrade head

# 운영 반영
uv run alembic upgrade head
```

---

## Java / Maven

**감지**: `pom.xml` 존재

### Lint / Format (Checkstyle)

```bash
mvn checkstyle:check
mvn spotless:check        # Spotless 사용 시
mvn spotless:apply        # 자동 포맷
```

### 단위 테스트

```bash
mvn test -pl <module>                    # 특정 모듈만
mvn test -Dtest=<TestClass>              # 특정 클래스만
mvn test -Dgroups="unit"                 # JUnit5 태그 기반
```

### 빌드

```bash
mvn clean package -DskipTests           # 테스트 스킵하고 빠르게 빌드
mvn clean package                       # 테스트 포함 전체 빌드
mvn clean install -DskipTests           # 로컬 repo에 설치
```

### Smoke Test

```bash
java -jar target/<app>-*.jar --dry-run 2>/dev/null || true
java -cp target/<app>-*.jar <MainClass> --version
```

### 배포

```bash
# 직접 실행
java -jar target/<app>-*.jar

# systemd
sudo systemctl restart <service-name>
```

### 정리

```bash
mvn clean
```

---

## Java / Gradle

**감지**: `build.gradle` 또는 `build.gradle.kts` 존재

### Lint / Format

```bash
./gradlew checkstyleMain checkstyleTest
./gradlew spotlessCheck
./gradlew spotlessApply        # 자동 포맷
```

### 단위 테스트

```bash
./gradlew test                             # 전체
./gradlew test --tests "<TestClass>"       # 특정 클래스
./gradlew test --tests "*.<method>"        # 특정 메서드
./gradlew test -PincludeTags="unit"        # 태그 기반
```

### 빌드

```bash
./gradlew clean build -x test   # 테스트 스킵하고 빠르게
./gradlew clean build           # 테스트 포함 전체
./gradlew assemble              # JAR/WAR만 생성
```

### Smoke Test

```bash
java -jar build/libs/<app>-*.jar --dry-run 2>/dev/null || true
```

### 배포

```bash
java -jar build/libs/<app>-*.jar

# systemd
sudo systemctl restart <service-name>
```

### 정리

```bash
./gradlew clean
```

---

## Spring Boot (Maven 또는 Gradle 위에 추가)

**감지**: `@SpringBootApplication` 어노테이션 + `pom.xml` 또는 `build.gradle`

> Maven 또는 Gradle 공통 명령 + 아래 Spring Boot 전용 명령을 함께 사용한다.

### 개발 서버 기동

```bash
# Maven
mvn spring-boot:run

# Gradle
./gradlew bootRun

# JAR 직접
java -jar target/<app>-*.jar   # Maven
java -jar build/libs/<app>-*.jar  # Gradle
```

### Smoke Test

```bash
curl -sf http://localhost:8080/actuator/health
curl -sf http://localhost:8080/actuator/info
```

### 통합 테스트

```bash
# Maven (@SpringBootTest 포함)
mvn verify -Dgroups="integration"

# Gradle
./gradlew integrationTest
./gradlew test -PincludeTags="integration"
```

### 마이그레이션 (Flyway / Liquibase)

```bash
# Flyway (Maven)
mvn flyway:info -Dflyway.url=<test-db-url>
mvn flyway:migrate -Dflyway.url=<test-db-url>

# Flyway (Gradle)
./gradlew flywayInfo
./gradlew flywayMigrate
```

### Docker 이미지 빌드 (Spring Boot 3+)

```bash
./gradlew bootBuildImage   # Buildpack 기반
mvn spring-boot:build-image
```

---

## React

**감지**: `package.json` + `react` 의존성

### Lint / Format

```bash
npx eslint src/ --fix
npx prettier --write src/

# 타입 체크 (TypeScript 사용 시)
npx tsc --noEmit
```

### 단위 테스트

```bash
# Jest (기본)
npm test -- --watchAll=false
npm test -- --coverage --watchAll=false

# Vitest 사용 시
npx vitest run
npx vitest run --coverage
```

### 빌드

```bash
npm run build           # 프로덕션 빌드
npm run build -- --mode development  # 개발 빌드

# 빌드 결과 확인
ls -lh dist/ || ls -lh build/
```

### 개발 서버 기동

```bash
npm start               # CRA
npm run dev             # Vite
```

### Smoke Test

```bash
# 개발 서버 응답 확인
curl -sf http://localhost:3000/ | grep -q "<!doctype html"

# 빌드 결과물 서빙 후 확인
npx serve -s build -p 3001 &
sleep 2
curl -sf http://localhost:3001/ | grep -q "<!doctype html"
kill %1
```

### 정리

```bash
rm -rf node_modules/.cache
rm -rf dist/ || rm -rf build/
```

---

## Node.js / JavaScript

**감지**: `package.json` (React 없음)

### Lint / Format

```bash
npx eslint . --fix
npx prettier --write .
```

### 단위 테스트

```bash
# Jest
npm test

# Mocha
npx mocha 'tests/**/*.test.js'

# Vitest
npx vitest run
```

### 빌드

```bash
npm run build           # 정의된 경우
npx tsc                 # TypeScript
```

### 개발 서버 기동

```bash
node src/index.js
npm run dev             # nodemon 등
```

### Smoke Test

```bash
curl -sf http://localhost:3000/health || curl -sf http://localhost:3000/
```

### 배포

```bash
# PM2
pm2 restart <app-name>
pm2 start src/index.js --name <app-name>

# systemd
sudo systemctl restart <service-name>
```

### 정리

```bash
rm -rf node_modules/.cache
```

---

## Docker Compose

**감지**: `docker-compose.yml` 또는 `docker-compose*.yml` 존재

> 언어별 빌드·테스트를 마친 뒤 컨테이너 교체 단계에서 사용한다.

### 테스트 스택 기동 (테스트용 compose 파일이 있는 경우)

```bash
# 이전 잔여물 정리
docker compose -f docker-compose.test.yml down --remove-orphans 2>/dev/null || true

# 변경된 서비스만 재빌드 후 기동
docker compose -f docker-compose.test.yml build <service>
docker compose -f docker-compose.test.yml up -d --no-deps <service>

# 상태 확인
docker compose -f docker-compose.test.yml ps
docker compose -f docker-compose.test.yml logs --tail=50 <service>
```

### Smoke Test (테스트 스택)

```bash
# 서비스별 포트는 프로젝트마다 다름 — docker-compose.test.yml 확인
curl -sf http://localhost:<test-port>/health
curl -sf http://localhost:<test-port>/
```

### 운영 스택 교체 (검증 통과 후에만)

```bash
# 특정 서비스만 교체
docker compose build <service>
docker compose up -d --no-deps <service>

# 의존 서비스 재시작이 필요한 경우 (nginx DNS 캐시 등)
docker compose restart <dependent-service>

# 전체 재빌드 (의존성 변경 시)
docker compose up -d --build

# 운영 상태 확인
docker compose ps
curl -sf http://localhost:<prod-port>/health
```

### 테스트 스택 정리

```bash
# 볼륨까지 완전 정리 (권장 — 포트 충돌 방지)
docker compose -f docker-compose.test.yml down --volumes

# 볼륨 보존이 필요한 경우만
docker compose -f docker-compose.test.yml down --remove-orphans
```

### 변경 파일 → 재빌드 대상 매핑 (일반 원칙)

| 변경 파일 | 재빌드 대상 |
|---|---|
| 앱 소스 코드 | 해당 서비스 이미지 |
| `Dockerfile` | 해당 서비스 이미지 |
| 의존성 파일 (`pom.xml`, `package.json`, `pyproject.toml` 등) | 해당 서비스 이미지 (전체 재빌드) |
| nginx 설정 (`nginx.conf`) | nginx / frontend 서비스 |
| 환경 변수 (`.env`) | 관련 서비스 재시작 |
| `docker-compose.yml` 자체 | `docker compose up -d` 전체 |

---

## Docker (단일 Dockerfile)

**감지**: `Dockerfile` 존재 (docker-compose 없음)

### 빌드

```bash
docker build -t <image-name>:<tag> .
docker build -t <image-name>:$(git rev-parse --short HEAD) .   # git SHA 태깅
```

### 기동 (테스트용)

```bash
docker run --rm -d \
  --name <container-name>-test \
  -p <test-port>:<container-port> \
  <image-name>:<tag>
```

### Smoke Test

```bash
docker ps | grep <container-name>-test
curl -sf http://localhost:<test-port>/health
```

### 운영 교체

```bash
docker stop <container-name> 2>/dev/null || true
docker rm <container-name> 2>/dev/null || true
docker run -d \
  --name <container-name> \
  --restart unless-stopped \
  -p <prod-port>:<container-port> \
  <image-name>:<tag>
```

### 정리

```bash
docker stop <container-name>-test 2>/dev/null || true
docker rm <container-name>-test 2>/dev/null || true
docker image prune -f   # dangling 이미지 정리
```

---

## Make 기반 프로젝트

**감지**: `Makefile` 존재

> Makefile 타겟 이름은 프로젝트마다 다르다. 아래는 관례적으로 자주 쓰이는 타겟이다.
> 실제 프로젝트에서는 `make help` 또는 `cat Makefile | grep "^[a-z]"` 로 타겟 목록을 먼저 확인한다.

### 타겟 확인

```bash
make help
# 또는
grep -E '^[a-zA-Z_-]+:' Makefile | cut -d: -f1
```

### 관례적 타겟

```bash
make lint       # lint 검사
make format     # 코드 포맷
make test       # 단위 테스트
make build      # 빌드
make run        # 실행
make clean      # 정리
make deploy     # 배포
make check      # lint + test 통합
make ci         # CI 전체 흐름
```

---

## Go

**감지**: `go.mod` 존재

### Lint / Format

```bash
gofmt -l ./...              # 포맷 불일치 파일 목록
gofmt -w ./...              # 자동 포맷
go vet ./...                # 정적 분석
golangci-lint run ./...     # 종합 lint (설치된 경우)
```

### 단위 테스트

```bash
# 전체
go test ./...

# 특정 패키지
go test ./internal/user/...

# 특정 함수
go test -run TestUserCreate ./...

# 커버리지
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out   # HTML 보고서
```

### 빌드

```bash
go build ./...                          # 전체 빌드 확인
go build -o bin/<app-name> ./cmd/<app>/ # 바이너리 생성
CGO_ENABLED=0 go build -o bin/<app-name> ./cmd/<app>/  # 정적 빌드 (컨테이너용)
```

### Smoke Test

```bash
./bin/<app-name> --version
./bin/<app-name> --dry-run 2>/dev/null || true
curl -sf http://localhost:8080/health
```

### 배포

```bash
# 직접 실행
./bin/<app-name>

# systemd
sudo systemctl restart <service-name>
```

### 정리

```bash
go clean ./...
rm -rf bin/
```

### tdd 스킬 파일 위치

- 소스: `internal/<package>/<file>.go`
- 테스트: `internal/<package>/<file>_test.go` (같은 디렉토리)

---

## Rust

**감지**: `Cargo.toml` 존재

### Lint / Format

```bash
cargo fmt --check          # 포맷 확인
cargo fmt                  # 자동 포맷
cargo clippy -- -D warnings  # lint (경고를 에러로)
```

### 단위 테스트

```bash
# 전체 단위 테스트 (통합 테스트 제외)
cargo test --lib

# 특정 테스트
cargo test test_<name>

# 통합 테스트 포함
cargo test

# 커버리지 (cargo-tarpaulin 설치 시)
cargo tarpaulin --out Html
```

### 빌드

```bash
cargo build              # 개발 빌드
cargo build --release    # 릴리즈 빌드 (최적화)
cargo check              # 컴파일 오류만 확인 (빠름)
```

### Smoke Test

```bash
./target/release/<app-name> --version
./target/release/<app-name> --help
```

### 배포

```bash
# 직접 실행
./target/release/<app-name>

# systemd
sudo systemctl restart <service-name>
```

### 정리

```bash
cargo clean
```

### tdd 스킬 파일 위치

- 소스·테스트 같은 파일 내 `#[cfg(test)] mod tests { ... }` 블록
- 통합 테스트: `tests/<test-name>.rs`

---

## Kotlin

**감지**: `*.kt` 파일 + (`build.gradle.kts` 또는 `pom.xml`)

> Gradle 또는 Maven 위에서 동작. 빌드 명령은 해당 섹션 참조.
> 아래는 Kotlin 전용 추가 사항이다.

### Lint / Format

```bash
# ktlint (독립 실행)
ktlint --format "src/**/*.kt"
ktlint "src/**/*.kt"

# Gradle 플러그인 (build.gradle.kts에 ktlint 설정 시)
./gradlew ktlintFormat
./gradlew ktlintCheck

# detekt (정적 분석)
./gradlew detekt
```

### 단위 테스트

```bash
# Gradle
./gradlew test -PexcludeTags="integration,slow"
./gradlew test --tests "*.UserServiceTest.*"

# Maven
mvn test -Dtest=UserServiceTest
```

### 빌드

```bash
# Gradle
./gradlew build -x test       # 테스트 스킵
./gradlew assemble

# Maven
mvn package -DskipTests
```

### Spring Boot + Kotlin

```bash
# 개발 서버
./gradlew bootRun

# Smoke Test
curl -sf http://localhost:8080/actuator/health

# 통합 테스트
./gradlew integrationTest
```

### tdd 스킬 파일 위치

- 소스: `src/main/kotlin/<package>/<Class>.kt`
- 테스트: `src/test/kotlin/<package>/<Class>Test.kt`
- JUnit5 어노테이션: `@Test`, `@Nested`, `@ExtendWith(MockitoExtension::class)`

---

## 멀티 스택 프로젝트 (예: Spring Boot + React + Docker Compose)

하나의 프로젝트에 여러 스택이 공존하는 경우:

1. **백엔드 루프**: Java/Spring Boot 섹션으로 빌드·테스트
2. **프론트엔드 루프**: React 섹션으로 빌드·테스트
3. **통합 루프**: Docker Compose 섹션으로 컨테이너 기동 후 smoke test

순서: 백엔드 단위 테스트 → 프론트엔드 단위 테스트 → 전체 Docker Compose 빌드 → 통합 smoke test → 운영 교체

```
예시 프로젝트 구조:
<root>/
├── backend/          → Spring Boot (Gradle)
│   └── build.gradle
├── frontend/         → React
│   └── package.json
└── docker-compose.yml
```
