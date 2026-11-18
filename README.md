# Fluxon 학습 안내 (예제 포함)

## 퀵 가이드
### 1. 개발자 따라하기 (https://demo.lumisware.com/live-fluxon) 과정을 완료하고
### 2. fluxon-getting-started의 소스를 다운로드 한 후,
### 3. 다음 순서대로 설정하면 바로 실행 결과를 확인할 수 있습니다.
#### 3.1. 라이브러리 함수 파일, 모듈 테스터 스크립트 설정 
- `temp` 폴더의 파일 2개(`temp/work_module_tester.sh`, `temp/work_lib.pyi`)를 파일을 프로젝트 폴더 외에 폴더로 이동합니다.
- 권장폴더) `~/temp/ref/work_module_tester.sh`, `~/temp/ref/work_lib.pyi`
- 예시폴더) `/Users/[your-name]/temp/ref/work_module_tester.sh`, `/Users/[your-name]/temp/ref/work_lib.pyi`
- 로컬 계정의 설정 shell 파일에 경로 등록 .zshrc  또는 .bash 등에 다음과 같이 추가
```text
alias worktest="$HOME/temp/ref/work_module_tester.sh"
```
- zsh라면
```text
source ~/.zshrc
```
- bash라면 수정한 파일에 맞게
```text
source ~/.bashrc
# 또는
source ~/.bash_profile
```

#### 3.2. backend 폴더의 소스 코드를 개발자 따라하기 도커에 연결하기
- 호스트 설치 경로 예시) /Users/your-name/fluxon-trial
- backend/demo_group 폴더를 fluxon-trial/fluxondemo/demo_group 폴더에 덮어쓰기 해주세요.

#### 3.3. backend 폴더에서 모듈 테스터 이용하기
- /Users/[your-name]/fluxon-trial/fluxondemo 폴더로 이동합니다.
- 모듈단위 테스트 진행하기
```text
$ worktest ExampleEcho
```
- 모듈단위 빌드 해보기(최초에만 .so 빌드 시에 2~5분 소요)
```text
$ worktest ExampleEcho deploy
```

#### 3.4. frontend
- **`frontend` 폴더의 터미널**에서 실행합니다.
```sh
npm ci
npm run dev
```
- 브라우저에서 http://localhost:5173 에서 접속 확인 가능합니다.
- 화면에서 "상품 관리", "워크 모듈 예제"에 대한 실행 예제를 확인할 수 있습니다.
- 화면 하단에 송수신되는 JSON을 확인할 수 있습니다. 해당 backend의 클래스를 찾아서 소스를 확인해 보세요.


## 개요
이 저장소에서는 **브라우저에서 요청 보내기 → Fluxon 워크 모듈 실행 → 결과 확인하기**를 배웁니다. 처음부터 모든 파일을 이해할 필요는 없습니다. 워크 모듈 예제의 DB 없는 ExampleEcho로 시작하고, 상품 관리와 공통 처리 코드를 차례로 읽어보세요.

실행 방법은 [frontend/README.md](./frontend/README.md), Python·SQL과 배포 방법은 [backend/README.md](./backend/README.md)에 있습니다. 이 문서는 학습 순서와 헷갈리기 쉬운 개념을 안내합니다.

[워크 모듈 기본 예제 12개](./backend/demo_group/examples/README.md)는 `service=examples`에서 실행합니다. DB 없는 입력·응답 예제 6개, 별도 테이블을 사용하는 MySQL·트랜잭션 예제 5개, 지연 처리 예제 1개로 구성했습니다. 상단 **워크 모듈 예제** 메뉴(`/examples`)에서 입력 JSON을 편집하고 각 예제의 마지막 송수신 JSON을 비교하세요. 기존 상품 화면은 `demo_service`를 유지합니다.

MySQL 학습 전에는 추가 준비 모듈 [ExampleMysqlSetup](./backend/demo_group/examples/src/ExampleMysqlSetup.py)을 명시적으로 호출합니다. 실습 테이블이 없으면 생성하고, 이미 있으면 기존 행과 ID를 유지합니다. DB 클라이언트에서 DDL을 직접 실행할 필요 없이 같은 Gateway 요청 방식으로 준비합니다.

이 준비는 `/examples`의 **ExampleMysqlSetup 실행** 버튼으로도 할 수 있습니다. 페이지에 접속하기만 해서는 어떤 워크 모듈도 호출하지 않습니다.

## 먼저 알아둘 구조

```text
브라우저의 Next.js 화면
  → Gateway에 JSON 요청
  → call 이름에 맞는 Python 워크 모듈 실행
  → 필요한 경우 MySQL 조회·변경
  → JSON 응답
  → React Query가 상태 갱신 → 화면·스낵바에 결과 표시
```

Next.js 서버는 화면과 공개 연결 설정을 제공합니다. API 요청은 브라우저가 Gateway에 직접 보내며 BFF를 거치지 않습니다. `backend` 폴더는 독립 Python 웹 서버가 아니라 Fluxon 워커에 반영할 모듈 모음입니다.

## 권장 학습 순서

| 순서 | 해볼 일 | 확인할 내용 |
| --- | --- | --- |
| 1. 송수신 | `/examples`에서 ExampleEcho를 선택하고 메시지를 전송합니다. | 송신 JSON의 `request_data.message`와 수신 JSON의 `response_data.result`를 비교합니다. |
| 2. 업무 실패 | 빈 메시지를 보냅니다. | HTTP 요청 완료와 업무 성공이 다르며 `ret_code`·`ret_msg`로 실패를 알리는 것을 봅니다. |
| 3. 상품 조회 | 데모 DB를 준비한 뒤 `/`에서 상품을 조회합니다. | `category`, `limit`, `sort`와 `{items, total}`의 관계를 봅니다. |
| 4. 등록 | 새 상품을 저장합니다. | 입력 검증은 백엔드가 담당하고 ID는 DB가 발급하는 것을 확인합니다. |
| 5. 수정·삭제 | 방금 등록한 상품을 수정·삭제합니다. | `id`로 대상을 지정하고 성공 후 목록을 다시 읽는 흐름을 봅니다. |
| 6. 오류와 복구 | 잘못된 분류나 음수 가격을 보냅니다. | 빨간 스낵바와 수정할 입력을 확인합니다. DB 작업 전 검증 위치도 읽습니다. |
| 7. 심화 | 공통 전송 코드를 읽습니다. | `cid` 결과 폴링, `waitMode`, 선택적 암호화를 배웁니다. |

**상품 화면은 첫 접속 때 AUTO_INCREMENT가 없는 테이블을 삭제·재생성할 수 있습니다.** 실습 전용 DB를 사용하세요. DB 없이 학습하는 1·2단계에서는 `/examples`의 ExampleEcho를 사용하면 됩니다. 초기화 버튼도 현재 상품 전체를 지우므로 일반 삭제와 구분하세요.

## 파일을 따라 읽는 방법

아래 경로는 저장소 루트 기준입니다. 코드에서 같은 함수 이름을 찾아 이동해 보세요.

### 첫 번째: DB 없는 작은 요청

1. [examples-runner.tsx](./frontend/app/examples/examples-runner.tsx): ExampleEcho를 선택하고 실행하면 `execution.mutate(...)`를 호출합니다.
2. [예제 client.ts](./frontend/src/features/examples/client.ts): 선택한 `ExampleEcho`를 실행하고 공통 업무 응답을 판정합니다.
3. [work-client.ts](./frontend/src/common/work-client.ts): `call`·`request_data`를 포함한 Gateway JSON을 만듭니다.
4. [ExampleEcho.py](./backend/demo_group/examples/src/ExampleEcho.py): 메시지 검사 후 `FLX_Return_Normal`로 결과를 반환합니다.
5. [gateway-response.ts](./frontend/src/common/gateway-response.ts): Gateway 오류와 업무 결과를 구분합니다.
6. [providers.tsx](./frontend/app/providers.tsx): 공통 스낵바를 표시합니다. 화면은 최종 응답을 JSON으로 보여줍니다.

### 두 번째: 입력을 DB에 저장하기

1. [product-form.tsx](./frontend/app/product-form.tsx): 상품 입력을 모읍니다. 빈 가격은 `null`로 보냅니다.
2. [상품 client.ts](./frontend/src/features/products/client.ts): `insertProduct`가 `ExampleInsert`를 호출합니다.
3. [ExampleInsert.py](./backend/demo_group/demo_service/src/ProductInsert.py): 입력 검증을 통과한 뒤 SQL을 실행합니다.
4. [flx_work_com.py](./backend/demo_group/svc_common/flx_work_com.py): 상품명·분류·가격을 검사하는 공통 함수를 읽습니다.
5. [ProductInsert_0.sql](./backend/demo_group/demo_service/sql/ProductInsert_0.sql): `:name` 등 값 바인딩과 ID 생략을 확인합니다.
6. [ExampleInsert_msg.json](./backend/demo_group/demo_service/msg/ProductInsert_msg.json): `ret_code`별 KOR·USA 메시지를 봅니다.
7. [product-query.tsx](./frontend/app/product-query.tsx): `response.code === 0`일 때만 목록을 갱신하는 부분을 읽습니다.

## 자주 헷갈리는 개념

| 개념 | 이 예제에서의 의미 |
| --- | --- |
| `call` / `request_data` | 실행할 워크 모듈 이름 / 그 모듈의 입력입니다. |
| `error_code` / `ret_code` | Gateway·런타임 오류 / 워크 모듈의 업무 결과입니다. 두 코드가 모두 0이어야 업무 성공입니다. |
| `useState` / React Query | 화면 입력·선택 상태 / 서버 데이터·요청 상태를 나누어 관리합니다. |
| `useQuery` / `useMutation` | 조회를 관리하는 도구 / 버튼으로 실행하는 요청을 관리하는 도구입니다. Echo도 `useMutation`을 씁니다. |
| `onSuccess` | 예외 없이 응답을 받았다는 뜻입니다. 업무 `code`도 따로 확인해야 합니다. |
| TypeScript / Zod | 개발 중 타입 검사 / 실행 중 들어온 실제 JSON의 구조 검사입니다. |
| 등록·수정 검증 | 백엔드 공통 함수가 담당합니다. 프런트엔드의 연결·조회·응답 구조 검사는 별도입니다. |
| React Query 캐시 / `cache_sec` | 브라우저에서 관리하는 조회 결과 / Gateway로 전달하는 결과 캐시 설정입니다. |
| `accepted` / `pending` | 접수됨 / 처리 중입니다. 최종 업무 성공·실패가 아닙니다. |
| 폴링 / 재시도 | 같은 `cid`의 결과만 다시 읽기 / 원래 업무 요청을 다시 보내기입니다. 이 예제는 쓰기 요청을 자동 재전송하지 않습니다. |
| `wait_sec` / `cancel` | Gateway의 응답 대기 시간 / 브라우저에서 대기 시간을 제한하는 선택 정책입니다. 서버 작업 취소는 아닙니다. |
| `mutation.reset()` / `ExampleReset` | React Query의 이전 요청 상태 비우기 / 실제 상품 테이블 삭제·재생성입니다. |
| `commit` / `rollback` | 일반 DB 변경 확정 / 아직 확정하지 않은 변경 취소입니다. DROP/CREATE로 삭제한 데이터는 rollback으로 복구되지 않습니다. |
| `src` / `exec` | 읽고 수정할 원본 / 실행용 폴더입니다. 원본 수정 후 런타임 반영 절차가 필요합니다. |

`queryKey`, `enabled`, `staleTime`, `refreshProducts()`를 한 번에 읽기 어렵다면 먼저 Echo의 `useMutation` 하나를 따라가세요. 그다음 상품 종류 자동 조회, 상품 목록 버튼 조회, 변경 후 재조회 순서로 나누면 됩니다. `payload-crypto.ts`의 암호화 내부 구현은 마지막에 읽어도 업무 흐름을 이해할 수 있습니다.

## 실습할 때의 주의점

- 현재 백엔드 파일은 `backend/demo_group/demo_service`, 요청 JSON도 `group=demo_group`, `service=demo_service`입니다. 프런트엔드 코드의 미설정 기본값은 `experience/products`이므로 `.env.local`에서 배포 위치를 명시하세요.
- `ProductInitialDB`는 AUTO_INCREMENT 여부를 읽고 `result=null` 또는 `"reset"`을 돌려줍니다. 프런트엔드가 `"reset"`일 때 `ExampleReset`을 한 번 호출하고 재점검합니다. 전체 스키마 검사나 데이터 보존 마이그레이션은 아닙니다.
- 신규 ID는 AUTO_INCREMENT로 발급합니다. 번호가 건너뛰어도 오류가 아니며, 목록의 연속 순번으로 사용하지 않습니다.
- 응답을 기다리다 중단해도 서버에서는 변경을 완료했을 수 있습니다. 목록·로그를 먼저 확인하고 같은 등록을 반복하지 마세요.
- `_msg.json`을 수정할 때는 KOR·USA에 같은 코드 집합을 유지합니다. API 필드명과 국가 코드를 한국어로 바꾸지는 않습니다.
- `if False` 아래의 고의 오류·지연 예제는 별도 실습을 위한 코드입니다. 정상 실행 흐름에 무심코 넣지 마세요.
- `.env.local`·개인키·토큰·실제 사용자 데이터를 공유하지 않습니다. 화면에 전달하는 연결 설정은 공개 정보입니다.
