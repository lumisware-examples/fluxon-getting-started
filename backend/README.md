# 백엔드 예제: 메시지 응답과 상품 관리

이 폴더는 Fluxon에서 실행할 Python **워크 모듈** 예제입니다. 워크 모듈은 Gateway가 요청의 `call` 이름으로 찾아 실행하는 작업 단위입니다. 먼저 DB가 필요 없는 `ExampleEcho`로 요청·응답을 익힌 뒤, 상품 조회·등록·수정·삭제를 살펴보세요.

Python 파일은 Fluxon 워커가 제공하는 `work_lib.FLXWork`를 사용합니다. 이 폴더에서 웹 서버를 별도로 실행하는 방식이 아닙니다. `python ExampleEcho.py`로 직접 실행하거나 이름이 같은 임의의 pip 패키지를 설치해 `work_lib`를 대신하지 마세요.

## 시작 전에 확인할 것

- 내 컴퓨터에 Fluxon Gateway와 워커가 설치되어 실행 중이어야 합니다.
- DB 없는 메시지 실습에는 `ExampleEcho`와 메시지 파일만 필요하며 MySQL은 사용하지 않습니다.
- 상품 관리에는 MySQL 연결, `fluxondemo` 스키마와 아래 상품 모듈들이 필요합니다.
- **상품 화면 최초 접속 때 `demo_products.id`에 AUTO_INCREMENT가 없으면 테이블을 삭제하고 다시 만듭니다. 기존 상품이 있는 업무용 DB에는 연결하지 마세요.** 이미 AUTO_INCREMENT이면 최초 준비 과정에서 초기화하지 않습니다.

프런트엔드 실행은 [프런트엔드 안내](../frontend/README.md), 전체 학습 순서는 [학습 안내](../README.md)를 참고하세요.

## 기능을 하나씩 배우는 12개 예제

[demo_group/examples/README.md](demo_group/examples/README.md)에 입력 검증·타입 변환·응답·설정·공통 함수·MySQL CRUD·트랜잭션·지연 처리 예제를 제공합니다. 요청 대상은 `service=examples`이며 기존 상품 관리의 `demo_service`와 구분합니다. 1–6번과 12번은 DB 없이 실행합니다. MySQL 예제는 추가 준비 모듈 [ExampleMysqlSetup](demo_group/examples/src/ExampleMysqlSetup.py)을 Gateway로 호출한 뒤 진행합니다. 이 모듈은 별도 `getting_started_example_items` 테이블을 CREATE TABLE IF NOT EXISTS로 준비하며 반복 실행해도 기존 행과 ID를 유지합니다. 자세한 호출 JSON과 배포 순서는 예제 README를 참고하세요.

프런트엔드 상단 **워크 모듈 예제** 메뉴(`/examples`)에서 준비 버튼과 예제별 실행·송수신 JSON을 사용할 수 있습니다. 페이지 접속이나 입력 예시 선택으로 API를 자동 실행하지 않습니다.

## 폴더와 요청 주소의 관계

```text
backend/
├── demo_group/                  # Gateway 요청의 group
│   ├── demo_service/            # Gateway 요청의 service
│   │   ├── src/                # 읽고 수정할 Python 원본
│   │   ├── sql/                # 워크 모듈이 번호로 불러오는 SQL
│   │   ├── msg/                # ret_code별 KOR·USA 메시지
│   │   ├── test/               # Gateway 요청 JSON 예시
│   │   └── exec/               # 실행용 파일을 두는 폴더
│   ├── svc_common/             # 그룹 안에서 공유하는 함수
│   └── svc_info/               # 서비스 설정 자료
└── tests/                      # 개발용 모의·통합 테스트
```

상품 예제 요청 JSON의 대상은 회사 `fluxondemo`, 그룹 `demo_group`, 서비스 `demo_service`입니다. 이 구조대로 배포했다면 프런트엔드의 `API_COM_CODE`, `API_GROUP`, `API_SERVICE`도 같은 값으로 맞춥니다. 폴더명과 요청 값이 다르면 모듈을 찾지 못하거나 다른 모듈을 호출할 수 있습니다.

`examples/test/ExampleEcho.json`은 **요청 데이터 예시**입니다. `tests/`의 Python 자동화 테스트와는 다릅니다.

## 1. DB 없이 메시지 주고받기

[ExampleEcho.py](demo_group/examples/src/ExampleEcho.py)와 [요청 JSON](demo_group/examples/test/ExampleEcho.json)을 나란히 읽어보세요.

```json
{
  "case": "work",
  "com_code": "fluxondemo",
  "group": "demo_group",
  "service": "examples",
  "call": "ExampleEcho",
  "c_code": "KOR",
  "request_data": { "message": "안녕하세요, Fluxon!" }
}
```

| 항목 | 의미 |
| --- | --- |
| `case` | `work`는 워크 모듈 실행 요청입니다. |
| `com_code` / `group` / `service` | 실행할 모듈이 속한 위치입니다. |
| `call` | 실행할 클래스 이름입니다. 여기서는 `ExampleEcho`입니다. |
| `c_code` | 백엔드 메시지의 국가 코드입니다. `KOR`는 한국어, `USA`는 영어입니다. |
| `request_data` | 워크 모듈에 전달할 입력입니다. |

코드는 입력 확인 → `message` 읽기 → 빈 값·길이 검사 → 응답 순서로 실행됩니다. 정상 문자열은 공백과 줄바꿈을 유지해 돌려줍니다. 공백만 있는 값이나 문자열이 아닌 값은 `ret_code=10`, Python 문자 수 기준 1000자 초과는 `11`입니다.

성공 시 `response_data`는 다음 형태입니다. 실제 Gateway 응답에는 바깥쪽 오류 코드 등도 포함됩니다.

```json
{
  "ret_code": 0,
  "ret_msg": "메시지를 받았습니다.",
  "result": "안녕하세요, Fluxon!"
}
```

## 2. 상품 모듈 읽기

아래 경로는 모두 `demo_group/demo_service/` 기준입니다.

| 모듈 | 입력 → 성공 결과 | 읽을 때 볼 부분 |
| --- | --- | --- |
| [ProductInitialDB](demo_group/demo_service/src/ProductInitialDB.py) | `{}` → `null` 또는 `"reset"` | ID 자동 발급 여부만 점검합니다. |
| [ProductReset](demo_group/demo_service/src/ProductReset.py) | `{}` → 초기화 완료 메시지 | 테이블 삭제 → 생성 → 예제 5개 등록입니다. |
| [ProductSelectCategories](demo_group/demo_service/src/ProductSelectCategories.py) | `{}` → `{categories: [...]}` | DB에서 중복 없는 상품 분류를 읽습니다. |
| [ProductInquiry](demo_group/demo_service/src/ProductInquiry.py) | `category`, `limit`, 선택 `sort` → `{items, total}` | 프런트엔드 목록 화면이 사용하는 조회입니다. |
| [ProductInsert](demo_group/demo_service/src/ProductInsert.py) | `name`, `category`, `price` → `{id}` | 검증 → INSERT → 발급 ID 확인 → commit입니다. |
| [ProductUpdate](demo_group/demo_service/src/ProductUpdate.py) | `id`, `name`, `category`, `price` → `{id}` | ID와 입력 검사 후 대상 상품을 수정합니다. |
| [ProductDelete](demo_group/demo_service/src/ProductDelete.py) | `id` → `{id}` | 해당 ID의 상품을 삭제합니다. |

`ProductInquiry`에서 `category: null`은 전체 분류, `limit`은 1–50개입니다. `sort` 생략 또는 `"id"`는 ID순, `"price_asc"`는 가격 오름차순입니다. `total`은 조회 조건에 맞는 전체 건수이며 `items`의 길이와 다를 수 있습니다.

### 입력 검증과 DB 작업

공통 함수는 [flx_work_com.py](demo_group/svc_common/flx_work_com.py)에 있습니다. 등록·수정은 이곳에서 상품명을 정리하고 다음 규칙을 검사한 뒤 DB에 접근합니다.

| 필드 | 규칙 |
| --- | --- |
| `name` | 앞뒤 공백 제거 후 필수, UTF-16 기준 80자 이하입니다. 일부 이모지는 2자로 셉니다. |
| `category` | 영문 대문자와 밑줄로 1–40자입니다. 소문자를 자동으로 바꾸지 않습니다. |
| `price` | 0–2147483647의 정수 값입니다. 숫자 문자열·불리언은 허용하지 않습니다. |
| `id` | 수정·삭제 시 1–2147483647의 정수입니다. |

등록·수정 폼에서 같은 업무 검증을 반복하지 않고, 서버가 돌려준 `ret_code`와 `ret_msg`로 결과를 알려줍니다. 수정·삭제할 ID가 없으면 `ret_code=10`입니다. 코드의 숫자는 모듈별 의미이므로 해당 `_msg.json`과 함께 확인하세요.

SQL의 `:name`, `:price` 등은 **값 바인딩** 자리입니다. 입력값을 SQL 문자열에 직접 이어 붙이지 않습니다. `{schema_name}`은 서버가 정한 스키마 이름을 넣는 별도 자리이며 사용자 입력을 받지 않습니다.

일반 쓰기는 `commit`으로 확정하고 예외가 나면 `rollback`합니다. `finally`에서는 성공·실패와 관계없이 DB 세션을 반환합니다. 등록 ID는 DB의 AUTO_INCREMENT와 INSERT 결과 `last_id`를 사용하므로 `MAX(id)+1`을 계산하지 않습니다. 삭제·실패 때문에 ID에 빈 번호가 생겨도 정상입니다.

### 최초 접속과 초기화

```text
ProductInitialDB: demo_products.id의 AUTO_INCREMENT 확인
  ├─ 있음 → ret_code=0, result=null → 상품 작업 허용
  └─ 없음/테이블 없음 → ret_code=0, result="reset"
       → 프런트엔드가 ProductReset 1회 호출
       → ProductInitialDB 재점검
```

`ProductInitialDB` 자체는 테이블을 바꾸지 않습니다. 초기화가 실패하거나 재점검에서도 `"reset"`이면 프런트엔드는 자동 반복하지 않습니다. 이 점검은 전체 테이블 구조를 검사하는 기능도 아닙니다.

`ProductReset_0.sql`은 DROP, `_1.sql`은 AUTO_INCREMENT 테이블 생성, `_2.sql`은 ID 1–5의 예제 등록입니다. 새 테이블에 예제 5개가 등록되면 다음 일반 등록 ID는 6입니다.

**DROP/CREATE는 MySQL에서 암시적으로 commit됩니다. 뒤의 INSERT가 실패해도 삭제 전 데이터가 rollback으로 돌아오지 않습니다.

## 메시지 파일과 오류 구분

예를 들어 [ProductInsert_msg.json](demo_group/demo_service/msg/ProductInsert_msg.json)은 `KOR`·`USA` 아래 같은 `ret_code` 키를 갖습니다. 요청의 `c_code`와 `ret_code`에 맞는 문구를 반환합니다. 메시지를 추가하면 두 언어를 함께 작성하세요. 메시지 없는 제어 응답만 보내는 `ProductInitialDB`는 메시지 파일이 없습니다.

- `error_code != 0`: Gateway·런타임 오류입니다. 프런트엔드에서 `error_msg`를 오류로 처리합니다.
- `error_code = 0`, `ret_code != 0`: 요청은 처리됐지만 업무가 실패했습니다. 프런트엔드는 `ret_msg`를 빨간 스낵바로 보여줍니다.
- 두 코드가 모두 0: 업무 성공이며 `ret_msg`를 초록 스낵바로 보여줍니다. 빈 메시지는 표시하지 않습니다.

## 모듈 테스터 - work_module_tester 설정
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

## 모듈 테스터 - work_module_tester 사용
- worktest 클래스명
```text
worktest ProductInquiry
```
- worktest 만 입력하여 사용 방법을 확인할 수 있습니다.
- 사용법
  /temp/ref/work_module_tester.sh [request_name] [test|deploy]
  /temp/ref/work_module_tester.sh com_build [그룹명[/서비스명]] 모듈명

업무 모듈 test/deploy 예
  /temp/ref/work_module_tester.sh ProductInquiry          # 기본 동작은 test
  /temp/ref/work_module_tester.sh ProductInquiry test     # Python 업무 모듈 실행 테스트
  /temp/ref/work_module_tester.sh ProductInquiry deploy   # 업무 모듈을 빌드해 exec에 저장

공통 모듈 빌드 예
  /temp/ref/work_module_tester.sh com_build  그룹명/서비스명  모듈명   # 서비스 범위
  /temp/ref/work_module_tester.sh com_build  그룹명  모듈명          # 그룹 범위
  /temp/ref/work_module_tester.sh com_build  모듈명                # 회사코드 범위
  회사코드는 컨테이너에서 읽고, 지정한 범위 아래의 svc_common을 사용합니다.
  모듈명에 .py를 생략하면 자동으로 붙입니다. AMD64·ARM64 .so는 원본 옆에 저장합니다.

## 런타임에 반영하기

먼저 위 파일들을 **자신의 데모 워커가 읽는 모듈 위치**에 배치하세요. 아래 명령은 컨테이너 이름이 `fluxon-demo-worker-fluxondemo-v10`, tester가 `/app/tester.py`, 모듈 루트가 `/app/modules/fluxondemo`인 환경 기준입니다. 명령이 로컬 저장소를 자동으로 복사해 주지는 않습니다.

예를 들어 원본은 `/app/modules/fluxondemo/demo_group/demo_service/src/ProductInsert.py`에 있어야 하며 `sql`·`msg`·`test`도 같은 서비스 아래에 둡니다. 실제 호스트 폴더는 Docker의 볼륨 연결 설정에서 확인하세요.

아래는 `examples` 서비스의 Echo 배포 명령입니다. 화면으로 메시지 실습을 시작하려면 배포 후 프런트엔드 `/examples`에서 ExampleEcho를 선택하세요.

```sh
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleEcho deploy
```

`src`를 수정해도 실행 중인 모듈이 자동으로 갱신되지는 않습니다.

원본 반영 후 빌드·배포하고, Docker Desktop의 `fluxon-demo > worker-fluxondemo-v10 > Logs`에서 처리 결과를 확인하세요.

공통 DB 함수는 현재 연결 이름 `MySQL`, 스키마 `fluxondemo`를 사용합니다. `ProductInquiry`는 런타임의 기본 저장소 이름을 사용하므로 이 값도 `fluxondemo`와 맞아야 합니다. `svc_info/mysql.json`만 바꿔 모든 모듈의 DB 설정이 바뀐다고 생각하지 마세요. 상품 초기화에는 메타데이터 조회와 DROP·CREATE·INSERT, 일반 작업에는 SELECT·INSERT·UPDATE·DELETE 권한이 필요합니다.

`if False` 아래 SQL 오류·지연 코드는 학습용이며 평소에는 실행되지 않습니다. `ProductInsert_1.sql`도 고의로 잘못된 컬럼을 사용하는 rollback 실습용입니다. 정상 SQL로 교체하거나 실서비스에서 활성화하지 마세요.
가