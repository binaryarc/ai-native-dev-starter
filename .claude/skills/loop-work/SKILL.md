---
name: loop-work
description: >
  어떤 언어·프레임워크든 개발→빌드→테스트→검증→배포 루프를 완주한다.
  Use when the user asks to implement a feature, fix a bug, or make any code change
  and wants it verified before applying — especially when they say
  "테스트 후 반영해", "테스트하고 올려줘", "검증하고 배포해", "확인 후 적용해",
  "안전하게 배포해", "테스트까지 해줘", "검증 후 반영", "테스트 후 배포",
  or any phrasing that implies develop → test → verify → deploy.
  Do NOT use for documentation-only changes or when the user explicitly says to skip testing.
argument-hint: "<작업 설명>"
type: skill
load: on-demand
---

# loop-work 스킬

작업이 완벽하게 검증될 때까지 **개발 → 빌드 → 테스트 → 검증** 루프를 반복하고,
통과 후에만 운영에 반영한다. 운영 환경은 검증 완료 전까지 절대 건드리지 않는다.

---

## 0. 시작 전 점검

```bash
git status                          # 현재 변경 상태 확인
git stash list                      # 미완료 작업 잔여물 확인
```

프로젝트에 `docs/ai-mistakes/lessons.md`가 있으면 읽는다.
이전 테스트/컨테이너 잔여물이 있으면 먼저 정리한다 (§3 참고).

---

## 0-A. 작업 분할 (복잡한 작업일 때만)

**단순 변경(파일 1~2개, 단일 목적)이면 이 단계를 건너뛴다.**

아래 기준 중 하나라도 해당하면 복잡한 작업이다:
- 변경 파일이 3개 이상이거나 여러 레이어에 걸침
- 독립적으로 구현·검증 가능한 하위 작업이 2개 이상
- DB 마이그레이션 + API + UI처럼 순서 의존성이 있는 작업

복잡한 작업이면:
1. `TaskCreate`로 하위 작업을 등록하고 의존성(`blockedBy`)을 설정한다.
2. 독립적인 태스크는 병렬로 진행한다.
3. 각 태스크 완료 시 `TaskUpdate`로 `completed` 표시 후 다음으로 넘어간다.

---

## 1. 개발

요청된 변경을 구현한다.
구현 후 즉시 § 언어별 lint/포맷 명령을 실행한다.
lint 오류가 남아 있으면 수정 후 **1단계로 돌아간다.**

---

## 2. 단위 테스트

§ 언어별 단위 테스트 명령을 실행한다.
실패하면 원인을 수정하고 **1단계로 돌아간다.**

---

## 3. 빌드 & 기동

§ 언어별 빌드 명령을 실행한다.
빌드 실패 또는 서비스 기동 실패 시 로그를 확인하고 **1단계로 돌아간다.**

---

## 4. Smoke Test

§ 언어별 smoke test 명령으로 서비스가 정상 응답하는지 확인한다.
실패하면 로그를 확인하고 **1단계로 돌아간다.**

---

## 5. 통합/기능 검증

- 새로 추가된 엔드포인트·기능이 의도대로 동작하는지 확인한다.
- DB 마이그레이션이 있으면 테스트 DB에서 먼저 확인한다.
- 문제가 발견되면 **1단계로 돌아간다.**

---

## 6. 운영 반영 (검증 통과 후에만)

**이 단계는 4·5단계를 모두 통과한 경우에만 실행한다.**

§ 언어별 배포 명령을 실행한다.
배포 후 smoke test를 다시 실행해 운영 환경을 확인한다.
실패하면 **1단계로 돌아간다.**

---

## 7. 테스트 환경 정리

§ 언어별 정리 명령으로 테스트 컨테이너·임시 파일을 제거한다.

---

## 8. 완료 처리

커밋 시 `hooks/pre-commit`이 lint·test·build를 자동 실행하므로 수동 재실행은 불필요하다.
프로젝트에 `/afterflight` 스킬이 있으면 실행한다.

---

## 9. 후속 과제 등록

작업 중 발견했지만 이번 범위 밖이라 미뤄둔 이슈가 있으면 `docs/todo.md` 또는 프로젝트 이슈 트래커에 추가한다.

---

## 루프 규칙

- 운영 환경은 검증 완료 전까지 절대 건드리지 않는다.
- 각 단계 실패 시 원인을 먼저 로그로 확인하고 1단계부터 재시작한다.
- 루프 횟수 제한 없음 — 완벽히 통과할 때까지 반복한다.

---

## § 언어별 명령 참조

프로젝트의 언어·프레임워크를 자동으로 감지한다 (파일 존재 여부 기준).
하나의 프로젝트에 여러 스택이 있으면 해당하는 모든 섹션을 적용한다.

→ 상세 명령은 [lang-profiles.md](./lang-profiles.md)를 참조한다.

### 빠른 감지 기준

| 감지 파일 | 스택 |
|---|---|
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python |
| `pyproject.toml` + FastAPI import | FastAPI |
| `pom.xml` | Java / Maven |
| `build.gradle` / `build.gradle.kts` | Java / Gradle |
| `pom.xml` + `@SpringBootApplication` | Spring Boot |
| `package.json` + React import | React |
| `package.json` (React 없음) | Node.js / JavaScript |
| `docker-compose*.yml` | Docker Compose |
| `Dockerfile` (단독) | Docker |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `*.kt` + `build.gradle.kts` | Kotlin / Gradle |
| `Makefile` | Make 기반 프로젝트 |
