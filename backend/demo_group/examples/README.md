# 기능별 워크 모듈 입문 예제 12개

`temp/work_lib.pyi`에 정의된 API를 작은 단위로 익히는 기본 예제 12개와 DB 준비 모듈 1개입니다. **1–6번과 12번은 DB 없이 실행**하고, 7–11번은 `ExampleMysqlSetup`으로 준비한 MySQL 실습 테이블을 사용합니다. 기존 `demo_service`의 상품 관리와 독립된 서비스입니다.

예제마다 Python 원본, KOR·USA 메시지, 기본 요청 JSON을 제공합니다. 실패·영어 요청은 [test/cases](test/cases)에 있습니다. 자동화 검증은 [backend/tests/test_examples.py](../../tests/test_examples.py)입니다.

## 준비와 폴더 구조

```text
examples/                     # Gateway service = examples
├── src/                      # 기본 예제 12개 + DB 준비 모듈 1개
├── sql/                      # 모듈이 불러오는 번호별 SQL
├── msg/                      # ret_code별 KOR·USA 문구
├── test/                     # 요청 JSON: 기본 요청과 cases의 추가 요청
├── svc_info/                 # 비밀값 없는 공개 실습 설정
├── svc_common/               # 이 서비스의 공통 함수
└── exec/                     # 빌드·배포 결과가 들어갈 위치
```

- Gateway와 Fluxon 워커가 실행 중이어야 합니다. Python 파일은 `work_lib.FLXWork` 기반이므로 독립 Python 웹 서버로 실행하지 않습니다.
- 요청 위치는 `com_code=fluxondemo`, `group=demo_group`, **`service=examples`**입니다. `call`은 아래 클래스 이름입니다.
- 소스는 워커의 `/app/modules/fluxondemo/demo_group/examples`에 반영합니다. 실제 호스트 경로와 컨테이너 이름은 자신의 설치 설정을 확인하세요.
- `src` 변경만으로 기존 실행 파일이 갱신되지는 않습니다. 아래 빌드·배포 절차를 따릅니다. `exec`에 원본을 복사해 배포를 대신하지 않습니다.
- 프런트엔드 상단 **워크 모듈 예제** 메뉴(`/examples`)에서 12개 기본 예제와 준비 모듈을 실행할 수 있습니다. 이 페이지는 `demo_group/examples`를 호출하며 상품 화면의 대상은 유지합니다. 메시지 송수신은 이 페이지의 ExampleEcho로 실습합니다. [프런트엔드 안내](../../../frontend/README.md)를 참고하세요.

## 화면으로 실행하기

1. 프런트엔드를 실행하고 [워크 모듈 예제](http://localhost:5173/examples)를 엽니다.
2. MySQL 예제 전에는 **ExampleMysqlSetup 실행**으로 테이블을 준비합니다. 페이지 접속으로 자동 생성하지 않습니다.
3. 예제와 준비된 입력을 선택하고 request_data JSON을 수정합니다.
4. **선택한 예제 실행**을 누르고 마지막 송신·수신 JSON과 스낵바를 확인합니다.

기본 입력·실패 입력 버튼은 값만 불러옵니다. KOR·USA 선택으로 메시지 언어를 비교할 수 있으며, 각 예제의 입력·마지막 결과는 페이지 안에서 전환해도 유지됩니다. 암호화 설정과 결과 폴링은 기존 공통 전송을 사용합니다. 아래 curl 방식으로도 같은 요청을 실행할 수 있습니다.

## 예제 목록과 학습 순서

| 순서 | 코드 | 배울 API·개념 | DB |
| --- | --- | --- | --- |
| MySQL 준비 | [ExampleMysqlSetup](src/ExampleMysqlSetup.py) | 실습 테이블 생성, 반복 실행 시 데이터 유지 | MySQL |
| 1 | [ExampleEcho](src/ExampleEcho.py) | `FLX_Get_Request_Data`, `FLX_Return_Normal` | 없음 |
| 2 | [ExampleValidation](src/ExampleValidation.py) | `FLX_Check_Request_Data`, 필수 키와 업무 값 검사 | 없음 |
| 3 | [ExampleTypeConversion](src/ExampleTypeConversion.py) | `FLX_Check_Request_Data`, `FLX_Type_Convert` | 없음 |
| 4 | [ExampleResponse](src/ExampleResponse.py) | `FLX_Return_Normal`, `FLX_Return_Error`, 메시지 치환 | 없음 |
| 5 | [ExampleConfig](src/ExampleConfig.py) | `FLX_Get_Info_Read`, `FLX_Get_Info_Values` | 없음 |
| 6 | [ExampleCommon](src/ExampleCommon.py) | `FLX_Call_Common_Func`, `FLX_Get_Common_Obj` | 없음 |
| 7 | [ExampleMySqlSelect](src/ExampleMySqlSelect.py) | 목록·단건·스칼라 SELECT, SQL 바인딩 | MySQL |
| 8 | [ExampleMySqlInsert](src/ExampleMySqlInsert.py) | INSERT, AUTO_INCREMENT, `last_id` | MySQL |
| 9 | [ExampleMySqlUpdate](src/ExampleMySqlUpdate.py) | `FOR UPDATE`, UPDATE, 대상 없음 | MySQL |
| 10 | [ExampleMySqlDelete](src/ExampleMySqlDelete.py) | 다른 모듈 SQL 재사용, DELETE | MySQL |
| 11 | [ExampleTransaction](src/ExampleTransaction.py) | INSERT 2개의 commit/rollback | MySQL |
| 12 | [ExampleDelayedResult](src/ExampleDelayedResult.py) | `FLX_Get_UUID`, 로그, Gateway 결과 폴링 | 없음 |

먼저 1–6번을 읽고, `ExampleMysqlSetup`을 호출한 뒤 **7번 조회 → 8번 등록 → 발급된 ID로 9번 수정 → 7번 확인 → 10번 삭제 → 11번 트랜잭션** 순서로 진행하세요. 12번은 DB 없이 별도로 실행할 수 있습니다.

## 요청 보내기

아래 명령은 저장소의 `backend` 폴더에서 실행합니다. Gateway 주소는 자신의 로컬 포트에 맞춥니다.

```sh
curl -X POST http://localhost:8100/v10/api \
  -H 'Content-Type: application/json' \
  --data-binary @demo_group/examples/test/ExampleEcho.json
```

기본 요청의 구조는 다음과 같습니다.

```json
{
  "case": "work",
  "com_code": "fluxondemo",
  "group": "demo_group",
  "service": "examples",
  "call": "ExampleEcho",
  "c_code": "KOR",
  "cache_sec": 0,
  "wait_sec": 10,
  "request_data": { "message": "안녕하세요, Fluxon!" }
}
```

`request_data`가 모듈의 입력입니다. `response_data.result`는 출력, `response_data.ret_code`·`ret_msg`는 업무 결과입니다. 예제 요청은 반복 실습 시 이전 결과가 재사용되지 않도록 Gateway 캐시를 0으로 둡니다.

아래에서 설명하는 `result`는 **최종 응답의 `response_data.result`**입니다. Gateway가 먼저 `accepted`·`pending`을 반환할 수도 있으며, 그 경우 같은 `cid`로 결과를 조회해야 합니다. HTTP 응답을 받은 것만으로 업무 성공을 판단하지 마세요.

## 1–6. DB 없는 기본 예제

### 1. ExampleEcho: 받은 메시지 반환

- [기본 요청](test/ExampleEcho.json): `{"message":"안녕하세요, Fluxon!"}` → `ret_code=0`, `result="안녕하세요, Fluxon!"`
- 공백·줄바꿈은 유지합니다. 공백만 있는 값·문자열 외 입력은 `10`, Python 문자 수 기준 1000자 초과는 `11`입니다.
- [빈 메시지 요청](test/cases/ExampleEcho.empty.json)으로 업무 실패 응답을 확인하세요.

### 2. ExampleValidation: 키 존재와 값 검사 구분

- [기본 요청](test/ExampleValidation.json): `{"name":"입문자","quantity":2}` → `result={"name":"입문자","quantity":2}`
- 필수 키 누락은 `FLX_Check_Request_Data`에서 Gateway `error_code=325`로 끝납니다.
- 키가 있으면 이름은 앞뒤 공백 제거 후 1–40자, 수량은 1–100의 정수인지 업무 코드로 검사합니다. 이름 오류는 `ret_code=10`, 수량 오류는 `11`입니다. `true`와 숫자 문자열은 정수로 인정하지 않습니다.
- [누락 요청](test/cases/ExampleValidation.missing.json)과 [범위 오류](test/cases/ExampleValidation.invalid.json)의 응답 계층을 비교하세요.

### 3. ExampleTypeConversion: 타입 변환

- [기본 요청](test/ExampleTypeConversion.json): `{"quantity":"2","enabled":"true","unit_price":"1000"}` → `result={"quantity":2,"enabled":true,"unit_price":1000}`
- `FLX_Check_Request_Data`는 요청 dict 안의 값을 바꾸고, `FLX_Type_Convert(..., data_set=...)`는 지정한 dict의 값을 바꿉니다.
- 변환 실패는 Gateway 오류입니다. 잘못된 불리언 문자열은 `326`, 숫자 변환 실패는 `327`입니다. 변환 후 수량·단가 범위 오류는 업무 코드 `10`·`11`입니다.
- 변환은 엄격한 업무 검증과 다릅니다. Python의 `int(1.9)`는 1이 됩니다. 실제 등록·수정처럼 원래 입력 타입을 엄격히 검사해야 할 때 변환만으로 검사하지 마세요.

### 4. ExampleResponse: 응답과 메시지

- [기본 요청](test/ExampleResponse.json): `outcome="success"` → `ret_code=0`, `result={"greeting":"입문자"}`, 이름이 포함된 메시지
- [실패 요청](test/cases/ExampleResponse.failure.json): `outcome="failure"` → `ret_code=10`, `result=null`
- [영어 요청](test/cases/ExampleResponse.usa.json): `c_code="USA"` → 같은 코드의 영어 메시지
- 이름 오류는 `11`, 잘못된 outcome은 `12`입니다. `FLX_Return_Error`도 **업무** `ret_code/ret_msg`를 반환합니다. 최상위 `error_code`를 만드는 함수로 혼동하지 마세요.
- 반환 함수는 현재 작업을 즉시 끝냅니다. DB 작업에서는 commit과 세션 반환을 마친 뒤 호출합니다.

### 5. ExampleConfig: 공개 설정 읽기

- [기본 요청](test/ExampleConfig.json): `{}` → `result={"title":"Fluxon 워크 모듈 입문","currency":"KRW","unit_price":1000}`
- [examples_lesson.json](svc_info/examples_lesson.json)에서 전체 설정을 읽고 `lesson.title`처럼 중첩 값을 꺼냅니다.
- 파일은 서비스 → 그룹 → 회사 범위로 검색합니다. 입력으로 임의 파일명을 받지 않으며 공개 실습 항목만 반환합니다. 비밀값을 넣지 마세요.
- 설정 파일 누락은 Gateway `221`, 설정 키 누락은 `217` 같은 런타임 오류입니다.

### 6. ExampleCommon: 공통 함수·객체

- [기본 요청](test/ExampleCommon.json): `{"unit_price":1000,"quantity":2}` → `result={"total":2000,"currency":"KRW"}`
- [examples_common.py](svc_common/examples_common.py)의 `calculate_total` 함수를 호출하고 `CURRENCY` 객체를 읽습니다.
- 단가 오류는 `ret_code=10`, 수량 오류는 `11`입니다. 공통 모듈은 이 `examples` 서비스 안에 두어 기존 상품 예제와 독립적으로 사용합니다.

## 7–11. MySQL 실습 준비

MySQL 풀 이름은 `MySQL`, 스키마는 워커의 `FLX_Get_Property_Default_StorageName`입니다. DB 준비 모듈 [ExampleMysqlSetup.py](src/ExampleMysqlSetup.py)가 [ExampleMysqlSetup_0.sql](sql/ExampleMysqlSetup_0.sql)을 읽어 실습 테이블을 생성합니다. SQL의 `{schema_name}`에는 워커의 기본 저장소 이름이 들어갑니다.

1. 사용하는 DB가 실습용인지 확인합니다.
2. 아래 배포 안내에 따라 그룹 공통 모듈 `flx_work_com`과 `ExampleMysqlSetup`·SQL·메시지를 반영합니다.
3. Gateway에 [ExampleMysqlSetup 요청](test/ExampleMysqlSetup.json)을 보냅니다. 입력 `request_data`는 빈 객체입니다.
4. 최종 응답의 `error_code=0`, `response_data.ret_code=0`과 준비 완료 메시지를 확인한 후 7–11번을 진행합니다.

`backend` 폴더에서 호출하는 예시입니다. 이 명령은 실제 실습 DB에 테이블을 생성하므로 대상 환경을 확인하고 실행하세요.

```sh
curl -X POST http://localhost:8100/v10/api \
  -H 'Content-Type: application/json' \
  --data-binary @demo_group/examples/test/ExampleMysqlSetup.json
```

성공하면 `response_data`에 다음 값이 담깁니다.

```json
{
  "ret_code": 0,
  "ret_msg": "실습 테이블 준비를 완료했습니다.",
  "result": { "table": "getting_started_example_items" }
}
```

`CREATE TABLE IF NOT EXISTS`이므로 반복 실행해도 기존 행과 ID를 유지합니다. 초기 데이터를 추가하거나 테이블을 삭제하지 않습니다. 기존 테이블의 잘못된 구조를 수정하는 마이그레이션도 아니므로 구조가 다르면 별도로 점검하세요. DB 스키마 자체는 미리 존재해야 합니다.

준비 모듈에는 CREATE 권한, 7–11번에는 SELECT·INSERT·UPDATE·DELETE 권한이 필요합니다. 다른 예제가 준비 모듈을 자동 호출하지 않으므로 직접 한 번 실행하세요. MySQL DDL은 암시적으로 commit되며 이후 오류가 나도 생성한 테이블이 rollback으로 사라지는 것은 아닙니다. 세션은 성공·실패 모두 반환합니다.

### 7. ExampleMySqlSelect: 세 가지 조회

- [기본 요청](test/ExampleMySqlSelect.json): `{"id":1,"limit":10}`
- 목록: `FLX_MySql_Select` → `items` 배열
- 단건: `is_get_one=True` → `item` 객체, 대상 없으면 `{}`
- 개수: `is_scalar=True` → `total` 숫자
- 빈 테이블의 성공 결과는 `{"items":[],"item":{},"total":0}`입니다. ID 오류는 `ret_code=10`, 조회 개수(1–50) 오류는 `11`입니다.
- 이 예제는 조회 API의 차이를 보여줍니다. 동시 변경 중 목록·개수의 일관성을 보장하는 별도 조회 정책은 다루지 않습니다.

### 8. ExampleMySqlInsert: ID 자동 발급

- [기본 요청](test/ExampleMySqlInsert.json): `{"name":"실습 노트","price":1000}` → `result={"id":발급된 정수}`
- 이름은 앞뒤 공백 제거 후 Python 문자 수 기준 1–80자, 가격은 0–2147483647의 정수로 검사합니다. 오류 코드는 이름 `11`, 가격 `12`입니다.
- SQL에서 ID를 생략하고 `is_get_last_id=True`로 같은 연결의 ID를 읽습니다. 발급 결과가 없으면 rollback하고 오류로 끝냅니다.
- **반환된 ID를 기록해 다음 수정·삭제 요청의 `id`에 넣으세요.** fixture의 1은 예시이며 실제 등록 ID를 보장하지 않습니다. 실패·삭제로 번호가 건너뛰어도 정상입니다.

### 9. ExampleMySqlUpdate: 대상 확인 후 수정

- [기본 요청](test/ExampleMySqlUpdate.json): `{"id":1,"name":"수정한 실습 노트","price":2000}` → `result={"id":1}`
- ID 오류는 `13`, 이름·가격 오류는 `11`·`12`, 대상 없음은 `10`입니다.
- `FOR UPDATE`로 대상 행을 확인한 뒤 같은 트랜잭션에서 수정합니다. 값이 원래와 같아도 대상이 있으면 성공입니다. 잠금은 InnoDB의 실제 동작이며 SQLite 모의 테스트에서는 검증하지 않습니다.

### 10. ExampleMySqlDelete: 한 행 삭제

- [기본 요청](test/ExampleMySqlDelete.json): `{"id":1}` → `result={"id":1}`
- `FLX_Other_Query_Load`로 `ExampleMySqlUpdate_0.sql`을 재사용합니다. Delete를 배포할 때 이 SQL도 필요합니다.
- ID 오류는 `13`, 대상 없음은 `10`입니다. `WHERE id = :id`로 요청한 행만 삭제합니다.

### 11. ExampleTransaction: 두 등록을 한 작업으로 처리

- [기본 요청](test/ExampleTransaction.json): `{"simulate_failure":false}` → `ret_code=0`, `result.committed=true`, 등록된 ID 2개
- [rollback 요청](test/cases/ExampleTransaction.rollback.json): `{"simulate_failure":true}` → `ret_code=10`, `result.committed=false`, `ids=[]`
- 두 번째 INSERT 뒤 학습용 예외를 발생시키면 두 등록이 함께 rollback됩니다. 이전에 저장된 실습 데이터는 유지합니다. 실제 SQL 오류는 업무 성공으로 숨기지 않고 다시 전달합니다.
- boolean이 아닌 simulate_failure는 `ret_code=11`입니다. `request_key`는 이번 실습의 로그·데이터 구분용 UUID이며 중복 등록 방지 키는 아닙니다.
- 이 예제의 일반 INSERT rollback과 테이블 DROP/CREATE의 암시적 commit은 다릅니다. DDL을 같은 방식으로 복원할 수 있다고 생각하지 마세요.

## 12. ExampleDelayedResult: 결과 폴링

[기본 요청](test/ExampleDelayedResult.json)은 `delay_sec=3`, `wait_sec=1`로 보냅니다. 워크 모듈은 DB 없이 3초를 기다리고 `result={"request_key":"UUID","delay_sec":3}`을 반환합니다. 지연 범위는 1–15초 정수이며 잘못된 값은 `ret_code=10`입니다.

Gateway가 먼저 `accepted` 또는 `pending`과 `cid`를 반환하면 다음 요청을 같은 Gateway로 보냅니다. 아래 cid는 **처음 응답에서 받은 실제 값으로 바꿉니다.** 워크 모듈의 `request_key`와 Gateway의 `cid`는 다릅니다.

```json
{
  "case": "result",
  "com_code": "fluxondemo",
  "cid": "처음 응답에서 받은 cid",
  "cache_sec": 0,
  "wait_sec": 1
}
```

`pending`이면 같은 cid로 결과만 다시 조회합니다. **원래 work 요청을 다시 보내지 않습니다.** 실행 타이밍에 따라 최초 응답부터 최종 결과가 올 수도 있습니다. accepted/pending/cid는 Gateway가 만들며 워크 모듈은 최종 업무 결과만 반환합니다.

자동 폴링 클라이언트로 호출할 때는 `waitMode=poll`을 사용하세요. 클라이언트의 응답 대기 중단과 서버 작업 취소는 별개입니다. 이 모듈은 서버 취소 API 예제가 아닙니다.

## 빌드·배포

아래는 기본 데모 컨테이너 이름과 tester 경로 기준입니다. **파일 반영 후** 실행하세요. 이 명령은 로컬 저장소를 워커로 복사하지 않습니다. 준비 모듈이 사용하는 그룹 공통 함수와 기본 예제의 서비스 공통 함수를 먼저 빌드합니다.

```sh
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py com_build fluxondemo/demo_group/svc_common/flx_work_com.py
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py com_build fluxondemo/demo_group/examples/svc_common/examples_common.py
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py com_build fluxondemo/demo_group/svc_common/examples_group_common.py
```

워크 모듈은 다음 명령으로 각각 배포합니다. 배포 후 위 Gateway 요청으로 `ExampleMysqlSetup`을 실행해 테이블을 준비합니다. 배포와 업무 호출은 별개입니다.

```sh
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleMysqlSetup deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleEcho deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleValidation deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleTypeConversion deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleResponse deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleConfig deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleCommon deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleMySqlSelect deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleMySqlInsert deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleMySqlUpdate deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleMySqlDelete deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleTransaction deploy
docker exec fluxon-demo-worker-fluxondemo-v10 python /app/tester.py fluxondemo demo_group examples ExampleDelayedResult deploy
```

배포 대상의 **회사·그룹·서비스를 명시한 위 명령**을 사용하세요. SQL·메시지·공개 설정·공통 모듈도 함께 반영하고 워커 Logs에서 결과를 확인합니다.

## 자동화 검증

`backend` 폴더에서 기본 예제 12개와 준비 모듈을 검사합니다.

```sh
python3 -B -m unittest discover -s tests -p test_examples.py -v
```

전체 기존 예제까지 검사하려면 다음 명령을 사용합니다.

```sh
python3 -B -m unittest discover -s tests -v
```

검증은 `work_lib` 모의 구현·메모리 SQLite로 실행합니다. 지연은 mock하므로 실제로 기다리지 않습니다. 테이블 준비·반복 준비 시 데이터 보존·오류 시 세션 정리와 입력 경계, 메시지 키, 값 바인딩, 대상 없음, last_id 누락, commit/rollback 실패를 검사합니다. 로컬에 `temp/work_lib.pyi`가 있으면 API 이름·키워드 인자도 대조합니다. 이 파일은 런타임 구현이 아니며 배포 필수 파일도 아닙니다.

실제 Gateway의 cid 발급·폴링, 워커 배포, MySQL 잠금·동시성 검증은 별도입니다. 이 테스트가 실제 DB를 초기화하거나 배포하지 않습니다.
