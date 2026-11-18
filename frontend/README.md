# 프런트엔드 예제: 상품 관리·워크 모듈

이 예제는 Next.js 화면에서 내 컴퓨터의 Fluxon Gateway를 호출하는 방법을 보여줍니다. **워크 모듈 예제**의 ExampleEcho로 DB 없이 요청·응답을 익힌 뒤, **상품 관리**에서 조회·등록·수정·삭제·초기화를 진행하세요.

상단 **워크 모듈 예제** 메뉴(`/examples`)에서는 기능별 예제 12개와 DB 준비 모듈을 선택해 실행할 수 있습니다.

UI는 Mantine, 서버 요청 상태는 TanStack Query(React Query), 타입은 TypeScript로 작성했습니다. 처음에는 화면 → API 호출 함수 → 백엔드 순서만 따라가고, 폴링과 암호화 구현은 나중에 읽어도 됩니다.

## 먼저 실행하기

Node.js 22 이상과 npm, 실행 중인 Fluxon Gateway·워커가 필요합니다. 워크 모듈 배포 방법은 [백엔드 안내](../backend/README.md)를 참고하세요. 이 프런트엔드가 백엔드 모듈을 자동으로 배포하지는 않습니다.

1. WebStorm 등에서 `frontend` 폴더를 엽니다.
2. **`frontend` 폴더의 터미널**에서 실행합니다.

```sh
npm ci
npm run dev
```

저장소 루트에서 시작했다면 먼저 `cd frontend`를 실행하세요. 브라우저에서 [워크 모듈 예제](http://localhost:5173/examples)를 엽니다. 종료는 터미널의 `Ctrl+C`입니다. 코드 변경은 개발 서버에 반영됩니다.

Windows PowerShell에서는 `npm run dev` 대신 다음처럼 실행합니다.

```powershell
npm ci
$env:NEXT_DIST_DIR = ".next-dev"
npx next dev -p 5173
```

**상품 관리(`/`)에 처음 접속할 때 ID 자동 발급 설정이 없으면 상품 테이블을 삭제·재생성합니다.** 기존 데이터를 보존해야 하는 DB에 연결하지 마세요. DB를 건드리지 않고 시작하려면 `/examples`에서 ExampleEcho를 먼저 실행하세요.

## Gateway 연결 설정

현재 저장소의 백엔드 폴더·요청 JSON에 맞춘 `.env.local` 예시는 다음과 같습니다.

```dotenv
API_SERVER=http://localhost:8100/v10/api
API_COM_CODE=fluxondemo
API_GROUP=demo_group
API_SERVICE=demo_service
API_COUNTRY_CODE=KOR
API_REQUEST_TIMEOUT_SEC=10
API_CACHE_SEC=10
```

| 설정 | 의미와 기본값 |
| --- | --- |
| `API_SERVER` | Gateway 주소입니다. 기본 `http://localhost:8100/v10/api`입니다. |
| `API_COM_CODE` | 회사 코드입니다. 기본 `fluxondemo`입니다. |
| `API_GROUP` | 배포한 그룹입니다. 코드 기본값은 `experience`지만 **현재 제공한 백엔드 폴더는 `demo_group`**이므로 위처럼 지정합니다. |
| `API_SERVICE` | 배포한 서비스입니다. 코드 기본값은 `products`지만 **현재 제공한 백엔드 폴더는 `demo_service`**입니다. |
| `API_COUNTRY_CODE` | 백엔드 메시지 언어를 선택합니다. 기본 `KOR`, 영어 메시지는 `USA`입니다. 화면 자체는 한국어입니다. |
| `API_REQUEST_TIMEOUT_SEC` | Gateway에 보내는 `wait_sec`입니다. 기본 10, 범위 0–60초입니다. 기본 대기 방식에서는 전체 작업의 시간 제한이 아닙니다. |
| `API_CACHE_SEC` | Gateway에 보내는 결과 캐시 시간입니다. 기본 10, 범위 0–60초입니다. React Query 캐시와는 별개입니다. |

설정을 바꿨다면 Next.js 서버를 재시작하세요. 설치한 모듈이 `experience/products`에 있다면 위 그룹·서비스를 그 배포 위치에 맞춥니다. 회사·그룹·서비스는 요청을 실행할 위치이므로 백엔드와 일치해야 합니다.

`config.ts`가 서버에서 이 값들을 읽고 필요한 공개 연결 설정만 화면에 전달합니다. `NEXT_PUBLIC_` 접두어는 필요하지 않습니다. **이 예제의 연결 설정은 브라우저에서도 볼 수 있으므로 비밀번호·개인키·인증 토큰을 넣지 마세요.** `.env.local`은 개인 실행 설정으로 관리하고 저장소에 커밋하지 않습니다.

연결 주소는 `localhost`, `127.0.0.1`, `::1`만 허용합니다. URL은 `/`, `/api`, `/v10/api` 경로를 입력할 수 있고 실제 요청은 `/v10/api`로 보냅니다. 이 예제는 로컬 학습을 위한 구성이며, 배포된 웹사이트에 접속한 사용자의 `localhost`는 그 사용자 자신의 컴퓨터입니다.

## 화면에서 해볼 일

### 워크 모듈 예제 `/examples`

1. 상단 **워크 모듈 예제** 메뉴를 선택합니다. 페이지 접속이나 예제 선택만으로 Gateway를 호출하지 않습니다.
2. MySQL 예제를 진행할 때 **ExampleMysqlSetup 실행**을 누릅니다. 전용 실습 테이블이 없으면 생성하고 기존 행과 ID는 유지합니다. DB 없는 예제는 이 준비 없이 실행합니다.
3. **실행할 예제**에서 모듈을 선택하고 기본 입력 또는 준비된 실패 입력을 불러옵니다.
4. **입력 JSON (request_data)**을 편집하고 **선택한 예제 실행**을 누릅니다. JSON 문법·객체 여부만 프런트엔드에서 확인하고 업무 값은 서버가 검사합니다.
5. 좌우의 **송신 JSON**과 **수신 JSON**을 비교합니다. 모바일에서는 위아래로 표시합니다.

각 예제의 마지막 송수신 기록과 편집 중인 입력은 이 페이지 안에서 예제를 바꿔도 유지됩니다. 송신 JSON은 마지막 실행 시점의 값이며 이후 입력을 바꿔도 그대로입니다. 같은 예제를 다시 실행하면 이전 수신 결과를 비우고 새 결과를 기다립니다. 다른 페이지로 이동하거나 새로고침하면 이 화면 기록은 초기화됩니다.

업무 실패도 수신 JSON으로 표시합니다. Gateway `error_code` 오류는 원래 오류 JSON과 오류 메시지를 보여주고, 네트워크 실패처럼 받은 JSON이 없으면 오류 설명만 표시합니다. 스낵바는 기존 공통 Provider의 규칙을 사용합니다.

이 페이지는 `.env.local`의 Gateway·회사·국가·대기·암호화 설정을 재사용하며, 그룹과 서비스는 제공한 백엔드 위치인 **`demo_group/examples`**로 고정합니다. `API_GROUP`·`API_SERVICE`를 변경해 상품 화면과 번갈아 설정할 필요가 없습니다. 요청 캐시는 0이며 **지연 처리 예제만 `wait_sec=1`**로 보내 결과 폴링을 확인합니다. 대기 정책은 공통 `waitMode`를 따릅니다.

입력 필드의 규칙·반환값·배포 방법은 [백엔드 예제 안내](../backend/demo_group/examples/README.md)를 참고하세요. 등록 후 반환된 `result.id`를 수정·삭제 입력에 넣습니다. 예제 입력을 불러오는 버튼은 API를 실행하지 않습니다.

### 상품 관리 `/`

화면 진입 시 다음 순서로 준비합니다.

```text
ProductInitialDB 호출
  ├─ result=null → 준비 완료
  └─ result="reset" → ProductReset 1회 → ProductInitialDB 재점검
준비 완료 → ProductSelectCategories로 상품 종류 조회
```

`ProductInitialDB`는 AUTO_INCREMENT 여부만 읽고, 테이블을 바꾸는 것은 `ProductReset`입니다. 초기화 실패나 재점검 실패에서 자동 반복하지 않습니다. 준비 중에는 작업을 잠그며, 실패하면 **준비 상태 다시 확인**으로 재확인할 수 있습니다.

| 탭 | 사용 방법 | 호출하는 워크 모듈 |
| --- | --- | --- |
| 조회 | 종류·최대 개수·정렬을 선택하고 상품 조회를 누릅니다. | `ProductInquiry` |
| 등록 | 상품명·분류·가격을 입력합니다. ID는 DB가 발급합니다. | `ProductInsert` |
| 수정 | 상품을 조회하고 행의 수정 버튼으로 폼을 엽니다. | `ProductUpdate` |
| 삭제 | 상품을 조회하고 대상 행에서 삭제를 확인합니다. | `ProductDelete` |
| 초기화 | 확인 창에서 실행하면 예제 상품 5개로 되돌립니다. 기존 상품은 삭제됩니다. | `ProductReset` |

탭 이동만으로 상품 목록을 추가 조회하지는 않습니다. 조회 조건과 결과는 탭 간 공유하고, 작성 중인 등록 폼도 유지합니다. 변경 성공 후에는 상품 종류와 목록을 다시 조회하며, 완료될 때까지 관련 입력·버튼·탭을 잠급니다.

조회에서 `ALL`은 `category: null`로 전달합니다. 최대 개수는 1–50, 정렬은 ID순 또는 가격 오름차순입니다. 표의 `total`은 조건에 맞는 전체 건수이며 표시된 행 수와 다를 수 있습니다. **수신 JSON**을 펼쳐 실제 응답을 확인하세요. 별도 학습 모듈인 `ExampleSelect`는 이 화면에서 사용하지 않습니다.

등록·수정의 필수값·형식·범위 검사는 백엔드가 담당합니다. 빈 가격은 `null`로 전달하며 서버 메시지를 보여줍니다. 프런트엔드에는 연결 설정·조회 조건·삭제 ID·수신 데이터 구조 검사가 남아 있습니다.

## 코드 읽기 순서

아래 경로는 `frontend/` 기준입니다.

| 파일 | 역할 |
| --- | --- |
| [app/examples/examples-runner.tsx](app/examples/examples-runner.tsx) | 선택한 모듈을 useMutation으로 실행하고 예제별 입력·송수신 기록을 관리합니다. |
| [src/features/examples/catalog.ts](src/features/examples/catalog.ts) | 13개 모듈의 설명과 기본·실패 입력입니다. 백엔드 요청 JSON과 맞춥니다. |
| [src/features/examples/client.ts](src/features/examples/client.ts) | 공통 callWork·serviceResult를 사용해 예제를 실행합니다. |
| [src/features/examples/config.ts](src/features/examples/config.ts) | 공개 연결 설정을 재사용하고 예제의 그룹·서비스를 고정합니다. |
| [src/common/work-client.ts](src/common/work-client.ts) | 공통 Gateway 요청 JSON을 만들고 전송 함수를 호출합니다. |
| [app/product-form.tsx](app/product-form.tsx) | 등록·수정에 공통으로 사용하는 입력 폼입니다. |
| [app/product-query.tsx](app/product-query.tsx) | 상품 탭, 준비 점검, 조회·변경·후속 갱신을 연결합니다. |
| [src/features/products/client.ts](src/features/products/client.ts) | 상품별 요청 함수를 정의합니다. `prepareProducts`도 여기에 있습니다. |
| [src/common/gateway-response.ts](src/common/gateway-response.ts) | Gateway 오류와 업무 결과를 구분합니다. |
| [app/providers.tsx](app/providers.tsx) | React Query 공통 설정과 요청 결과 스낵바를 연결합니다. |
| [src/features/products/model.ts](src/features/products/model.ts) | TypeScript 타입과 실제 JSON을 검사하는 Zod 스키마입니다. |
| [src/features/products/config.ts](src/features/products/config.ts) | 서버 환경변수와 기본 대기 방식을 읽습니다. |
| [src/features/products/transport.ts](src/features/products/transport.ts) | 공통 HTTP POST, 결과 폴링, 응답 대기 정책입니다. |
| [src/common/payload-crypto.ts](src/common/payload-crypto.ts) | 선택 설정인 요청·응답 암호화 구현입니다. 심화 과정에서 읽으세요. |

`app/page.tsx`와 `app/examples/page.tsx`는 서버에서 공개 설정을 읽어 브라우저 화면에 넘깁니다. **실제 API 호출은 브라우저 → Gateway로 직접 진행**하며, Next.js API Route·Server Action·BFF·프록시를 사용하지 않습니다. 그래서 Gateway의 CORS 설정도 필요합니다.

## React Query는 무엇을 담당하나요?

React의 `useState`는 입력값·선택 탭·모달 같은 화면 상태를, React Query는 서버 데이터와 요청 상태를 담당합니다.

| API·상태 | 이 예제에서의 사용 |
| --- | --- |
| `useQuery` | DB 준비 점검·상품 종류·상품 목록 조회를 관리합니다. 최초 준비에는 조건부 초기화도 포함됩니다. |
| `queryKey` | 결과를 구분하는 캐시 이름입니다. 조회 조건이 다르면 다른 결과로 관리합니다. |
| `enabled` | 조회 실행 조건입니다. 목록은 `false`로 두고 버튼에서 `refetch()`합니다. |
| `useMutation` / `mutate` | Echo 전송과 상품 변경, 워크 모듈 예제의 수동 실행을 관리합니다. |
| `isFetching` / `isPending` | 각각 조회 중 여부, mutation 처리 중 여부를 표시하는 데 사용합니다. |
| `invalidateQueries` / `refetch` | 변경 후 이전 조회를 무효화하고 최신 데이터를 가져옵니다. |

`useMutation.onSuccess`가 호출되어도 업무 성공이라는 뜻은 아닙니다. 정상 응답 안의 `code`가 0인지 확인한 뒤에만 갱신합니다. 상품 mutation은 후속 조회도 `await`하므로 목록 갱신이 끝날 때까지 처리 중 상태가 유지됩니다.

React Query의 자동 재시도와 창 포커스·네트워크 복구 시 자동 재조회는 꺼두었습니다. 상품의 **준비 점검 → 조건부 초기화 → 재점검**도 자동 반복하지 않습니다. 업무 요청을 다시 보내는 재시도와 아래 `cid` 결과 조회는 다른 동작입니다.

## 요청과 결과 폴링 흐름

실제 `fetch`는 `transport.ts`의 `post()` 한 곳에서 실행합니다. Echo와 상품 요청 모두 같은 경로를 사용합니다.

```text
화면 → client.ts → callWork → gatewayRequest
  → case: "work" 전송 1회
  → 바로 최종 결과면 종료
  → status: "accepted" 또는 "pending" + cid
      → 같은 cid로 case: "result" 조회
      → pending이면 결과 조회만 반복
      → 최종 응답 → 업무 결과 판정 → 스낵바·화면 갱신
```

결과 조회에는 최초 `cid`, `com_code`, `cache_sec`, `wait_sec`를 보냅니다. 응답에 `cid`가 생략돼도 최초 값을 유지하며 다른 값이 오면 오류로 처리합니다. **등록 등의 `work` 요청을 반복하는 것이 아닙니다.** Gateway가 `wait_sec` 동안 기다린 뒤 응답하는 전제로 결과 응답 후 다음 조회를 바로 보냅니다.

`config.ts`의 `waitMode` 기본값은 `poll`입니다. `gatewayRequest()`에 생략하거나 `undefined`를 전달해도 같습니다.

| 방식 | 동작 |
| --- | --- |
| `poll` | 최종 결과 또는 오류까지 기다립니다. 총 시간·횟수 제한이나 강제 AbortSignal을 넣지 않습니다. `wait_sec=0`도 즉시 취소를 뜻하지 않습니다. |
| `cancel` | 한 요청 흐름의 최초 전송부터 후속 결과 조회까지 `wait_sec`(1–60초)를 공유하고, 지나면 브라우저 응답 대기를 중단합니다. |

`cancel`은 **서버 작업을 취소하는 API가 아닙니다.** 변경 도중 대기가 끝나도 DB 작업은 완료됐을 수 있으므로 목록·로그부터 확인하고 같은 등록을 바로 재전송하지 마세요.

암호화를 켜면 먼저 `security/security/security`에서 공개키를 받고 `request_data`만 암호화합니다. 이때 `request_data.secure`는 `true`입니다. 최종 응답을 검증·복호화하며 실패했다고 평문으로 재전송하지 않습니다. 공개키 조회와 업무 요청은 각각 별도 대기 흐름입니다. 평문 모드는 공개키 조회·암복호화를 생략합니다.

## 성공·실패 메시지는 어디에서 표시하나요?

`gateway-response.ts`가 응답을 판정하고 `providers.tsx`의 `QueryCache`·`MutationCache` 공통 콜백이 스낵바를 표시합니다.

| 응답 | 처리 |
| --- | --- |
| `error_code != 0` | `error_msg`로 예외를 만들고 빨간 스낵바로 표시합니다. |
| `error_code = 0`, `response_data.ret_code != 0` | 업무 실패입니다. 예외로 바꾸지 않고 `ret_msg`를 빨간 스낵바로 표시합니다. |
| 두 코드 모두 0 | 업무 성공입니다. `ret_msg`를 초록 스낵바로 표시하고 필요한 조회를 갱신합니다. |
| `ret_msg`가 비어 있음 | 임의의 알림 문구를 만들지 않습니다. |
| HTTP·네트워크 오류 또는 잘못된 JSON 구조 | React Query의 오류 상태와 빨간 스낵바로 처리합니다. |

## 연결되지 않을 때

| 증상 | 확인할 곳 |
| --- | --- |
| 연결 실패 | Docker Desktop에서 `fluxon-demo > gateway-v10`, `worker-fluxondemo-v10` 실행 상태와 Gateway 포트를 확인합니다. |
| 워크 모듈을 찾지 못함 | `.env.local`의 회사·그룹·서비스·`call`과 실제 배포 위치를 비교합니다. 특히 `experience/products` 기본값과 `demo_group/demo_service`를 구분하세요. |
| 브라우저 CORS 오류 | Gateway에서 `http://localhost:5173` Origin과 POST·OPTIONS, `Content-Type`을 허용하는지 확인합니다. |
| 상품 준비 오류 | `ProductInitialDB`·`ProductReset`, 공통 모듈, SQL 반영, MySQL 연결과 권한을 확인합니다. |
| 암호화 오류 | Gateway 공개키 서비스와 암호화 설정을 확인합니다. 오류를 숨기기 위해 자동 평문 재전송을 추가하지 마세요. |
| 처리가 오래 걸림 | 기본 `poll`은 계속 기다립니다. 워커 Logs에서 해당 `call`과 요청 시각을 확인하세요. |

브라우저가 로컬 네트워크 접근 권한을 요청하면 내 Gateway 접속에 필요한 권한인지 확인하고 허용하세요. 포트가 이미 사용 중이면 기존 서버를 확인하고, 포트를 바꾼 경우 Gateway의 허용 Origin도 맞춥니다.

## 코드 검사와 빌드

아래 명령은 모두 `frontend` 폴더에서 실행합니다.

```sh
npm run lint
npm run typecheck
npm run build
npm start
```

`lint`는 코드 규칙, `typecheck`는 TypeScript 타입, `build`는 배포용 빌드를 확인합니다. `npm start`는 빌드 후 실행하는 서버이며 개발 서버 명령이 아닙니다. 이 검사들은 실제 Gateway·MySQL 동작을 대신 검증하지 않습니다.

다음 학습 주제와 어려운 코드의 읽는 방법은 [학습 안내](../docs/README.md)에서 확인하세요.
