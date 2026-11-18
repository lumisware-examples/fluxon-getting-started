from abc import ABCMeta, abstractmethod
from typing import Any, NoReturn, Sequence

JsonDict = dict[str, Any]

import datetime as _datetime

DEBUG: int
INFO: int
WARNING: int
ERROR: int
CRITICAL: int

class FLXWork(metaclass=ABCMeta):
    def __init__(self, **args) -> None: ...

    # --------------------------------------------------------------------
    @abstractmethod
    def FLX_Main_Field_Check(self) -> None:
        """처리를 시작하기 전에 요청값을 검사하는 메서드이다.

        FLXWork를 상속한 업무 클래스에서 반드시 작성한다.

        - 검사할 항목이 없으면 메서드 안에 pass를 작성한다.

        사용 예

        .. code-block:: python

            def FLX_Main_Field_Check(self) -> None:
                self.FLX_Check_Request_Data("order_id", int)
        """
        ...

    # --------------------------------------------------------------------
    @abstractmethod
    def FLX_Main_Work_Start(self) -> None:
        """요청받은 업무를 처리한다.

        일반적으로 결과 회신은 다음과 같이 한다.

        - 정상 처리 완료 : FLX_Return_Normal()에 결과를 전달한다.
        - 처리 오류 : FLX_Return_Error()에 코드와 메시지를 전달한다.

        일반 return을 사용하면 Frontend에 전달되지 않는다.

        사용 예

        .. code-block:: python

            def FLX_Main_Work_Start(self) -> None:
                order_id = self.FLX_Get_Request_Data("order_id")
                if order_id <= 0:
                    self.FLX_Return_Error(1001, "주문 번호는 양수여야 합니다.")
                self.FLX_Return_Normal({"order_id": order_id})
        """
        ...

    # --------------------------------------------------------------------
    @property
    def FLX_Get_Property_ComCode(self):
        """현재 요청의 회사 코드인 com_code를 읽는다.

        속성(property)이므로 이름 뒤에 괄호를 붙이지 않고 사용한다.

        **반환값**

        요청에 담긴 com_code. 예를 들어 "my_company"이다.

        사용 예

        .. code-block:: python

            com_code = self.FLX_Get_Property_ComCode
        """
        ...

    # --------------------------------------------------------------------
    @property
    def FLX_Get_Property_Default_StorageName(self):
        """현재 회사와 실행 환경에 맞는 표준 저장소 이름을 조회한다.

        DB 스키마명이나 S3 버킷명에 쓸 이름을 얻을 때 사용한다.

        **반환값**

        회사 코드와 환경 접미사를 합친 문자열.

        사용 예

        .. code-block:: python

            storage_name = self.FLX_Get_Property_Default_StorageName

        회사 코드가 mycompany일 때

        - src, int, dev → mycompanydev
        - stg → mycompanystg
        - demo, prod → mycompany
        """
        ...

    # --------------------------------------------------------------------
    @property
    def FLX_Get_Property_CCode(self):
        """현재 요청의 국가·언어 구분 값인 c_code를 읽는다.

        속성(property)이므로 이름 뒤에 괄호를 붙이지 않고 사용한다.
        Frontend가 보낸 c_code는 업무 결과의 언어별 메시지를 찾을 때도 사용된다.

        **반환값**

        요청에 담긴 c_code. 예를 들어 "KOR"이다. 생략한 요청의 기본값은 빈 문자열이다.

        사용 예

        .. code-block:: python

            c_code = self.FLX_Get_Property_CCode  # 요청이 c_code="KOR"이면 "KOR"
        """
        ...

    # --------------------------------------------------------------------
    def FLX_LOG(self, level, msg, *args, exc_info=None) -> None:
        """업무 처리 중 확인할 내용을 서버 로그에 남긴다.

        메시지 앞에 Worker ID와 업무명을 붙인다. 버전과 회사 코드도 로그 정보에 포함한다.
        로그가 실제로 출력되는 범위는 서버의 로그 레벨 설정에 따른다.

        **인자**

        - ``level`` — DEBUG, INFO, WARNING, ERROR, CRITICAL 중 하나.
        - ``msg`` — 로그에 남길 문장. 값이 들어갈 자리에 %s 또는 %d 등을 쓸 수 있다.
        - ``*args`` — msg의 %s, %d 등에 순서대로 넣을 값. 예를 들어 %s가 하나면 값도 하나를 전달한다.
        - ``exc_info`` — 예외가 발생한 코드 위치와 함수 호출 경로(traceback)를 로그에 남길지 지정한다.
          WARNING, ERROR, CRITICAL에서 적용한다.

        **반환값**

        None. 기록한 내용은 서버 로그에서 확인한다.

        사용 예

        .. code-block:: python

            self.FLX_LOG(INFO, "주문 조회 order_id=%s", order_id)

            try:
                quantity = int("잘못된 값")
            except ValueError:
                self.FLX_LOG(ERROR, "수량을 숫자로 바꿀 수 없습니다.", exc_info=True)
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Return_Error(self, ret_code: int, ret_msg: str = '', is_traceback: bool = False, **msg_params) -> NoReturn:
        """업무 리턴 코드와 메시지를 Frontend에 전달하고 현재 업무를 끝낸다.

        응답의 업무 결과는 Frontend에서 response_data.ret_code와 response_data.ret_msg로 확인한다.

        **인자**

        - ``ret_code`` — 개발자가 정하는 리턴 코드. 예를 들어 1001을 사용할 수 있다.
        - ``ret_msg`` — Frontend에 보낼 메시지. 기본값은 빈 문자열이다.
          서비스의 msg/<call>_msg.json에 요청의 c_code와 ret_code에 맞는 문구가 있으면 그 문구를 사용한다.
          파일을 읽을 수 없거나 문구가 없으면 ret_msg를 사용한다.
        - ``is_traceback`` — True를 주면 현재 예외가 발생한 위치와 함수 호출 경로도 로그에 남긴다.
        - ``**msg_params`` — 메시지 파일 문구의 {field} 등에 넣을 값.
          예를 들어 파일에 "{field} 값이 잘못되었습니다."가 있으면 field="order_id"를 전달한다.

        사용 예

        .. code-block:: python

            self.FLX_Return_Error(1001, "주문 번호는 양수여야 합니다.")
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Return_Normal(self, _return: Any | None = None, ret_code: int = 0, ret_msg: str = '', **msg_params) -> NoReturn:
        """처리 결과를 Frontend에 전달하고 현재 업무를 끝낸다.

        **인자**

        - ``_return`` — Frontend가 받을 실제 데이터. response_data.result에 담긴다.
          dict, list, 문자열, 숫자, bool 등 JSON으로 바꿀 수 있는 값을 전달한다.
          생략하거나 None이면 기존 result 값을 사용한다. 처음의 result 값은 None이다.
        - ``ret_code`` — 업무 결과 번호. 기본값 0은 성공을 뜻한다.
        - ``ret_msg`` — Frontend에 보낼 기본 결과 문장. 기본값은 빈 문자열이다.
          서비스의 msg/<call>_msg.json에 요청의 c_code와 ret_code에 맞는 문구가 있으면 그 문구를 사용한다.
          파일을 읽을 수 없거나 문구가 없으면 ret_msg를 사용한다.
        - ``**msg_params`` — 메시지 파일 문구의 {order_id} 등에 넣을 값.
          파일 문구에 필요한 치환 값이 빠졌을 때도 기본 ret_msg를 사용한다.

        사용 예

        .. code-block:: python

            self.FLX_Return_Normal({"order_id": 123}, ret_msg="조회 완료")
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Check_Request_Data(self, field_name: str | None = None, convert_type: Any = None, is_exist: bool = True) -> None:
        """요청의 request_data에 필요한 값이 있는지 검사하고, 필요하면 타입을 바꾼다.

        FLX_Main_Field_Check()에서 주로 사용한다. 변환한 값은 원본 request_data에 저장된다.

        **인자**

        - ``field_name`` — 검사할 키 이름. "order_id"처럼 쓰거나 "user.id"처럼 점으로 이어 쓴다.
          "user.id"는 {"user": {"id": "123"}} 안의 id를 뜻한다.
        - ``convert_type`` — int, str, float, bool 등 변환할 타입. 기본값 None은 키가 있는지만 검사한다.
          값이 None이나 빈 문자열이어도 키가 있으면 존재 검사를 통과한다.
          bool은 문자열 "true"/"false"를 공백과 대소문자를 무시해 변환한다.
          다른 문자열은 326 오류이며, 숫자나 None 등에는 bool(value)를 적용한다.
        - ``is_exist`` — 기본값 True는 반드시 있어야 하는 필드로 검사한다.
          False는 선택 필드이며 키가 없거나 중첩 경로에서 dict가 아닌 값을 만나면 건너뛴다.
          선택 필드도 이름 형식과 찾은 값의 변환 과정은 검사한다.

        **반환값**

        None. 검사가 끝나면 다음 업무 코드를 실행한다. 변환된 값은 원본 request_data에 저장된다.

        사용 예

        .. code-block:: python

            # 필수 값. 문자열 "123"을 정수 123으로 변환
            self.FLX_Check_Request_Data("order_id", int)
            # 선택 값. notify가 있을 때만 bool로 변환
            self.FLX_Check_Request_Data("notify", bool, is_exist=False)
            # 중첩 값. user 안의 id를 정수로 변환
            self.FLX_Check_Request_Data("user.id", int)

        Frontend에 전달되는 오류

        검사에 실패하면 업무를 끝내고 응답의 최상위 error_code와 error_msg로 아래 값을 Frontend에 전달한다.
        Frontend에서는 error_code가 0보다 클 때 오류로 처리한다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 322
             - 요청 데이터 형식이 올바르지 않습니다.
             - request_data가 dict가 아님
           * - 323
             - 필드명이 비어 있습니다.
             - 필드명이 비어 있거나 문자열이 아님
           * - 324
             - '{필드명}' 필드 경로가 올바르지 않습니다.
             - user..id처럼 빈 구간이 있거나 필수 경로의 중간 값이 dict가 아님
           * - 325
             - 필수 항목 {필드명}이(가) 없습니다.
             - 필수 키가 없음
           * - 326
             - '{필드명}'의 값이 true 또는 false가 아닙니다.
             - bool로 바꿀 문자열이 true/false가 아님
           * - 327
             - 요청 필드의 값을 지정한 형식으로 변환할 수 없습니다.
             - 변환 중 TypeError 또는 ValueError 발생
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Type_Convert(self, field_name: str, convert_type: Any, data_set: dict | None = None) -> None:
        """dict 안의 값 하나를 원하는 타입으로 바꾸어 같은 dict에 저장한다.

        예를 들어 {"quantity": "3"}에서 문자열 "3"을 숫자 3으로 바꿀 때 사용한다.
        변환할 dict를 지정하거나, 현재 요청의 request_data를 대상으로 사용할 수 있다.

        **인자**

        - ``field_name`` — 바꿀 값의 최상위 키. 예를 들어 "quantity"이다.
          점이 들어간 "user.id"도 그 이름의 키 하나로 찾는다.
          중첩된 요청값은 FLX_Check_Request_Data("user.id", int)처럼 처리한다.
        - ``convert_type`` — int, str, float, bool 등 변환할 타입이나, 값 하나를 받아 변환한 값을 반환하는 함수.
          bool은 문자열 true/false를 앞뒤 공백과 대소문자를 무시해 변환한다.
          다른 문자열은 오류이고, 문자열 이외의 값은 bool(value)로 변환한다.
        - ``data_set`` — 변환할 dict. 생략하거나 None이면 현재 요청의 request_data를 사용한다.

        **반환값**

        None. 바뀐 값은 data_set 또는 현재 요청의 request_data에 저장된다.

        사용 예

        .. code-block:: python

            data = {"quantity": "3"}
            self.FLX_Type_Convert("quantity", int, data_set=data)
            quantity = data["quantity"]  # 숫자 3

        Frontend에 전달되는 오류

        변환에 실패하면 업무를 끝내고 응답의 최상위 error_code와 error_msg로 아래 값을 Frontend에 전달한다.
        메시지의 {필드명}에는 실제 필드명이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 322
             - 요청 데이터 형식이 올바르지 않습니다.
             - 변환 대상이 dict가 아님
           * - 325
             - 필수 항목 {필드명}이(가) 없습니다.
             - 지정한 키가 없음
           * - 326
             - '{필드명}'의 값이 true 또는 false가 아닙니다.
             - bool로 바꿀 문자열이 true/false가 아님
           * - 327
             - 요청 필드의 값을 지정한 형식으로 변환할 수 없습니다.
             - 변환 중 TypeError 또는 ValueError 발생
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_Request_Data(self, field: str | None = None, convert_type: Any | None = None) -> Any | None:
        """Frontend가 보낸 request_data 전체 또는 그 안의 값 하나를 읽는다.

        {"order_id": "123"} 같은 dict에서 값을 꺼낼 때 사용한다.
        request_data 전체를 받으면 원본을 참조하므로, 그 dict를 수정하면 현재 요청 데이터에도 반영된다.

        **인자**

        - ``field`` — 읽을 최상위 키. 예를 들어 "order_id"이다. 생략하거나 None이면 request_data 전체를 받는다.
        - ``convert_type`` — int, str, bool 등 값을 바꿀 타입. 지정하면 필수 키 검사와 변환을 거친 뒤 값을 읽는다.
          변환 결과는 원래 request_data에도 저장된다. 생략하면 값을 그대로 읽는다.

        **반환값**

        field에 해당하는 값. 변환 없이 읽을 때 키가 없으면 None이다.
        field가 None이거나 request_data가 dict가 아니면 원본 request_data를 반환한다.

        중첩된 값 사용 시 주의

        이 함수의 최종 조회는 최상위 키 하나를 대상으로 한다.
        "user.id"를 지정하면 최상위에 이름이 "user.id"인 키를 찾는다.
        변환 타입을 함께 지정하면 검사 함수는 점을 중첩 경로로 해석한다.
        그 결과 안쪽 user의 id가 변환되어도 최상위 "user.id" 키가 없으면 반환값은 None이다.
        중첩 값을 읽을 때는 아래처럼 검증 후 dict에서 직접 꺼낸다.

        사용 예

        .. code-block:: python

            request_data = self.FLX_Get_Request_Data()
            order_id = self.FLX_Get_Request_Data("order_id", int)
            # 중첩 요청값을 사용할 때
            self.FLX_Check_Request_Data("user.id", int)
            user_id = request_data["user"]["id"]

        Frontend에 전달되는 오류

        dict에서 변환 타입을 지정하여 읽을 때 검사에 실패하면, 업무를 끝내고
        error_code와 error_msg로 아래 값을 Frontend에 전달한다.
        형 변환 없이 읽을 때 키가 없으면 None을 반환한다.
        메시지의 {필드명}에는 실제 필드명이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 323
             - 필드명이 비어 있습니다.
             - 형 변환을 요청한 필드명이 비어 있거나 문자열이 아님
           * - 324
             - '{필드명}' 필드 경로가 올바르지 않습니다.
             - user..id처럼 빈 구간이 있거나 중첩 경로의 중간 값이 dict가 아님
           * - 325
             - 필수 항목 {필드명}이(가) 없습니다.
             - 형 변환할 키가 없음
           * - 326
             - '{필드명}'의 값이 true 또는 false가 아닙니다.
             - bool로 바꿀 문자열이 true/false가 아님
           * - 327
             - 요청 필드의 값을 지정한 형식으로 변환할 수 없습니다.
             - 변환 중 TypeError 또는 ValueError 발생
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_Info_Read(self, file_name: str):
        """svc_info 폴더의 파일을 읽는다. 서비스 → 그룹 → 회사코드 순서로 검색해 처음 발견한 파일을 사용한다.

        **인자**

        - ``file_name`` — 확장자를 포함한 파일명.

        **반환값**

        올바른 .json 파일은 파싱한 값으로 반환한다. 일반 파일과 파싱할 수 없는 .json 파일은 UTF-8 문자열로 반환한다.

        **사용 예**

        .. code-block:: python

            content = self.FLX_Get_Info_Read("settings.json")

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 221
             - 파일을 찾을 수 없습니다.
             - 파일이 검색 경로에 없음
           * - 222
             - 파일을 UTF-8로 읽을 수 없습니다.
             - 파일을 UTF-8로 읽을 수 없음
           * - 223
             - 파일을 읽을 수 없습니다.
             - 읽기 중 다른 오류가 발생함
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_Info_Values(self, info_name: str | dict, field_names: str | list[str]):
        """정보 파일 또는 dict에서 원하는 값만 꺼낸다. "db.host"처럼 점으로 연결하면 dict 안의 dict를 차례대로 조회한다.

        **인자**

        - ``info_name`` — svc_info 파일명 또는 값을 꺼낼 dict. 파일은 JSON 객체 형태여야 한다.
        - ``field_names`` — 필드명 하나 또는 비어 있지 않은 필드명 리스트.

        **반환값**

        필드명 하나를 주면 해당 값 하나를, 리스트를 주면 지정한 순서대로 값 리스트를 반환한다.

        **사용 예**

        .. code-block:: python

            info = {"db": {"host": "localhost", "port": 3306}}
            host = self.FLX_Get_Info_Values(info, "db.host")
            values = self.FLX_Get_Info_Values(info, ["db.host", "db.port"])

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 214
             - 필드명이 비어 있습니다.
             - 필드명이 빈 문자열이거나 문자열이 아님
           * - 215
             - '{필드명}' 필드 경로가 올바르지 않습니다.
             - db..host처럼 경로에 빈 구간이 있음
           * - 216
             - '{필드명}' 필드 경로가 올바르지 않습니다.
             - 경로 중간 값이 dict가 아님
           * - 217
             - '{필드명}' 필드가 없습니다.
             - 경로에 해당 키가 없음
           * - 218
             - '{파일명}'가 dict가 아닙니다.
             - 파일에서 읽은 값이 dict가 아님
           * - 219
             - info_name은 파일명(str) 또는 dict여야 합니다.
             - 정보 원본의 타입이 잘못됨
           * - 220
             - field_names는 필드명(str) 또는 비어 있지 않은 list[str]이어야 합니다.
             - 필드명 인자가 문자열이나 비어 있지 않은 리스트가 아님
           * - 221
             - 파일을 찾을 수 없습니다.
             - 파일이 검색 경로에 없음
           * - 222
             - 파일을 UTF-8로 읽을 수 없습니다.
             - 파일을 UTF-8로 읽을 수 없음
           * - 223
             - 파일을 읽을 수 없습니다.
             - 읽기 중 다른 오류가 발생함
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_Template_Read(self, file_name: str):
        """svc_template 폴더의 파일을 읽는다. 서비스 → 그룹 → 회사코드 순서로 검색해 처음 발견한 파일을 사용한다.

        **인자**

        - ``file_name`` — 확장자를 포함한 파일명.

        **반환값**

        올바른 .json 파일은 파싱한 값으로 반환한다. 일반 파일과 파싱할 수 없는 .json 파일은 UTF-8 문자열로 반환한다.

        **사용 예**

        .. code-block:: python

            content = self.FLX_Get_Template_Read("notice.txt")

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 221
             - 파일을 찾을 수 없습니다.
             - 파일이 검색 경로에 없음
           * - 222
             - 파일을 UTF-8로 읽을 수 없습니다.
             - 파일을 UTF-8로 읽을 수 없음
           * - 223
             - 파일을 읽을 수 없습니다.
             - 읽기 중 다른 오류가 발생함
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_Common_Obj(self, module_name: str, attr_name: str) -> Any:
        """svc_common에서 함수, 클래스, 설정값 등 이름이 붙은 객체를 가져온다. 서비스 → 그룹 → 회사코드 순서로 모듈을 찾는다.

        **인자**

        - ``module_name`` — 공통 모듈 이름. 예를 들어 pricing.py의 이름은 pricing이다.
        - ``attr_name`` — 모듈 안에서 가져올 객체의 이름(함수, 클래스 등).

        **반환값**

        가져온 객체.

        **사용 예**

        .. code-block:: python

            obj_func = self.FLX_Get_Common_Obj("pricing", "calculate_total")
            result = obj_func(1000, quantity=2)

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 208
             - 공통 모듈 객체를 찾을 수 없습니다: {모듈명}.{객체명}
             - 모듈 또는 지정한 객체를 찾지 못함
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Call_Common_Func(self, module_name: str, func_name: str, *args: Any, **kwargs: Any) -> Any:
        """svc_common에 있는 함수를 호출한다.

        **인자**

        - ``module_name`` — 공통 모듈 이름.
        - ``func_name`` — 실행할 함수 이름.
        - ``*args`` — 함수에 순서대로 전달할 값.
        - ``**kwargs`` — 함수에 이름을 붙여 전달할 값.

        **반환값**

        공통 함수가 반환한 값.

        **사용 예**

        .. code-block:: python

            total = self.FLX_Call_Common_Func("pricing", "calculate_total", 1000, quantity=2)

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 208
             - 공통 모듈 객체를 찾을 수 없습니다: {모듈명}.{객체명}
             - 모듈 또는 지정한 객체를 찾지 못함
           * - 209
             - 공통 모듈 실행 함수를 찾을 수 없습니다: {모듈명}.{함수명}
             - 가져온 객체를 함수처럼 호출할 수 없음
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_UUID(self, use_dash: bool = False) -> str:
        """식별자로 사용할 키(UUID)를 만든다.

        **인자**

        - ``use_dash`` — True이면 하이픈을 포함한다. 기본값은 False이다.

        **반환값**

        UUID 문자열.

        **사용 예**

        .. code-block:: python

            request_key = self.FLX_Get_UUID(use_dash=True)
        """
        ...

    # --------------------------------------------------------------------
    @staticmethod
    def FLX_Hash_Password(password: str, iterations: int = 200000) -> str:
        """비밀번호를 저장용 해시 문자열로 바꾼다. 같은 비밀번호도 호출할 때마다 다른 임의 값인 salt를 사용한다.

        **인자**

        - ``password`` — 입력받은 비밀번호 문자열.
        - ``iterations`` — PBKDF2-HMAC-SHA256 반복 횟수. 기본값은 200000이다.

        **반환값**

        알고리즘과 반복 횟수, salt, 해시가 포함된 저장용 문자열.

        **사용 예**

        .. code-block:: python

            saved_hash = self.FLX_Hash_Password(password)
        """
        ...

    # --------------------------------------------------------------------
    @staticmethod
    def FLX_Verify_Password(raw_password: str, saved_password: object) -> bool:
        """입력한 비밀번호가 저장된 해시와 맞는지 확인한다.

        **인자**

        - ``raw_password`` — 입력받은 비밀번호 문자열.
        - ``saved_password`` — FLX_Hash_Password()로 만든 저장용 문자열.

        **반환값**

        일치하면 True를 반환한다. 불일치하거나 저장값의 형식을 읽을 수 없으면 False를 반환한다.

        **사용 예**

        .. code-block:: python

            is_valid = self.FLX_Verify_Password(password, saved_hash)
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Auth_Token_Create(self, subject: str, data: dict, ttl_seconds: int | None = None) -> None:
        """새 인증 토큰을 만들고 업무 응답의 최상위 auth_token에 담는다.

        **인자**

        - ``subject`` — 토큰의 용도를 나타내는 제목.
        - ``data`` — 토큰에 저장할 JSON으로 변환 가능한 dict.
        - ``ttl_seconds`` — 유효기간을 초로 지정한다. 생략하거나 None이면 1800초이다.

        **반환값**

        None. 생성한 인증 토큰은 응답으로 전달된다.

        **사용 예**

        .. code-block:: python

            self.FLX_Auth_Token_Create("login", {"user_id": user_id})
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Auth_Token_Update(self, token: str | None = None, ttl_seconds: int | None = None, overwrite_data: dict | None = None) -> None:
        """인증 토큰을 갱신해 업무 응답의 최상위 auth_token에 담는다.

        **인자**

        - ``token`` — 갱신할 토큰 문자열. 생략하면 현재 인증 토큰을 사용한다.
        - ``ttl_seconds`` — 유효기간을 초로 지정한다. 생략하거나 None이면 1800초이다.
        - ``overwrite_data`` — 새로 저장할 dict. None이면 기존 토큰의 데이터를 사용한다.

        **반환값**

        None. 사용할 인증 토큰이 있으면 갱신한 토큰이 응답에 담긴다.

        **사용 예**

        .. code-block:: python

            self.FLX_Auth_Token_Update(ttl_seconds=3600)

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 301
             - 토큰 값이 빈값입니다.
             - 빈 토큰을 전달함
           * - 302
             - 유효하지 않은 토큰입니다.
             - 토큰 검증에 실패함
           * - 303
             - 토큰 오류입니다.
             - 토큰 내용을 JSON으로 읽지 못함
           * - 304
             - 토큰의 payload가 비정상입니다.
             - 토큰 내용이 dict가 아님
           * - 305
             - 토큰 만료 시간 설정 오류입니다.
             - 만료 시각이 정수가 아님
           * - 306
             - 토큰이 만료되었습니다.
             - 현재 시각이 만료 시각에 도달함
           * - 307
             - 토큰 제목이 없습니다.
             - 기존 제목이 빈 값이거나 문자열이 아님
           * - 308
             - 토큰에 저장할 Data가 비정상입니다.
             - 새로 저장할 데이터가 dict가 아님
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Other_Token_Create(self, subject: str, data: dict, ttl_seconds: int | None = None) -> str:
        """auth_token 외에 다른 용도로 사용할 토큰을 만든다.

        **인자**

        - ``subject`` — 토큰의 용도를 나타내는 제목.
        - ``data`` — 토큰에 저장할 JSON으로 변환 가능한 dict.
        - ``ttl_seconds`` — 유효기간을 초로 지정한다. 생략하거나 None이면 1800초이다.

        **반환값**

        새 토큰 문자열.

        **사용 예**

        .. code-block:: python

            token = self.FLX_Other_Token_Create("order", {"order_id": 123})
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Other_Token_Update(self, token: str, ttl_seconds: int | None = None, overwrite_data: dict | None = None) -> str:
        """임의의 용도로 생성한 토큰을 검증하고 유효기간을 갱신한다.

        **인자**

        - ``token`` — 갱신할 토큰 문자열.
        - ``ttl_seconds`` — 유효기간을 초로 지정한다. 생략하거나 None이면 1800초이다.
        - ``overwrite_data`` — 새로 저장할 dict. None이면 기존 토큰의 데이터를 사용한다.

        **반환값**

        갱신된 토큰 문자열.

        **사용 예**

        .. code-block:: python

            new_token = self.FLX_Other_Token_Update(token, ttl_seconds=3600)

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 301
             - 토큰 값이 빈값입니다.
             - 빈 토큰을 전달함
           * - 302
             - 유효하지 않은 토큰입니다.
             - 토큰 검증에 실패함
           * - 303
             - 토큰 오류입니다.
             - 토큰 내용을 JSON으로 읽지 못함
           * - 304
             - 토큰의 payload가 비정상입니다.
             - 토큰 내용이 dict가 아님
           * - 305
             - 토큰 만료 시간 설정 오류입니다.
             - 만료 시각이 정수가 아님
           * - 306
             - 토큰이 만료되었습니다.
             - 현재 시각이 만료 시각에 도달함
           * - 307
             - 토큰 제목이 없습니다.
             - 기존 제목이 빈 값이거나 문자열이 아님
           * - 308
             - 토큰에 저장할 Data가 비정상입니다.
             - 새로 저장할 데이터가 dict가 아님
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_Token_Payload(self, field: str | None = None, token: str | None = None) -> Any:
        """토큰에 저장한 데이터를 읽는다.

        **인자**

        - ``field`` — 토큰의 data 안에서 읽을 키 하나. 생략하면 토큰의 전체 내용을 읽는다.
        - ``token`` — 조회할 토큰 문자열. 생략하면 현재 인증 토큰(auth_token)을 사용한다.

        **반환값**

        field를 주면 해당 값을 반환한다. 생략하면 subject, data, insert_at, expire_at, jwt_id가 들어 있는 dict를 반환한다.

        **사용 예**

        .. code-block:: python

            user_id = self.FLX_Get_Token_Payload("user_id")
            payload = self.FLX_Get_Token_Payload()

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 301
             - 토큰 값이 빈 값입니다.
             - 토큰 인자와 현재 인증 토큰이 모두 None임
           * - 301
             - 토큰 값이 빈값입니다.
             - 빈 토큰을 전달함
           * - 302
             - 유효하지 않은 토큰입니다.
             - 토큰 검증에 실패함
           * - 303
             - 토큰 오류입니다.
             - 토큰 내용을 JSON으로 읽지 못함
           * - 304
             - 토큰의 payload가 비정상입니다.
             - 토큰 내용이 dict가 아님
           * - 305
             - 토큰 만료 시간 설정 오류입니다.
             - 만료 시각이 정수가 아님
           * - 306
             - 토큰이 만료되었습니다.
             - 현재 시각이 만료 시각에 도달함
           * - 309
             - 토큰에서 {필드명} 정보가 없습니다.
             - data에 해당 키가 없거나 값이 None임
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Query_Load(self, query_num: int, replace_items: dict | None = None) -> str | None:
        """현재 서비스의 sql 폴더에서 <call>_<번호>.sql 파일을 읽는다.

        **인자**

        - ``query_num`` — 파일명 끝에 붙는 번호.
        - ``replace_items`` — 치환할 문구와 새 문구를 담은 dict. 예를 들어 {"{table}": "orders"}를 전달한다. SQL 값은 실행 함수의 바인딩 인자로 전달한다.

        **반환값**

        읽어 온 SQL 문자열.

        **사용 예**

        .. code-block:: python

            query = self.FLX_Query_Load(1)

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 353
             - SQL 파일을 불러올 수 없습니다.
             - 파일 읽기 또는 문자열 치환 실패. 치환 검증 오류 351·352는 같은 cid의 Worker 로그에서 확인한다.
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Other_Query_Load(self, req_name: str, query_num: int, com_code: str | None = None, req_group: str | None = None, req_service: str | None = None, replace_items: dict | None = None) -> str | None:
        """지정한 회사·그룹·서비스의 sql 폴더에서 다른 업무의 SQL을 읽는다.

        **인자**

        - ``req_name`` — 파일명 앞부분에 쓰이는 업무 이름.
        - ``query_num`` — 파일명 끝에 붙는 번호.
        - ``com_code`` — 회사 코드. 생략하면 현재 회사.
        - ``req_group`` — 그룹명. 생략하면 현재 그룹.
        - ``req_service`` — 서비스명. 생략하면 현재 서비스.
        - ``replace_items`` — 치환할 문구와 새 문구를 담은 dict. 예를 들어 {"{table}": "orders"}를 전달한다. SQL 값은 실행 함수의 바인딩 인자로 전달한다.

        **반환값**

        읽어 온 SQL 문자열.

        **사용 예**

        .. code-block:: python

            query = self.FLX_Other_Query_Load("order_lookup", 1, req_service="orders")

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 353
             - SQL 파일을 불러올 수 없습니다.
             - 파일 읽기 또는 문자열 치환 실패. 치환 검증 오류 351·352는 같은 cid의 Worker 로그에서 확인한다.
        """
        ...

    # --------------------------------------------------------------------
    def FLX_IsCancel(self):
        """현재 요청의 취소 신호를 확인한다. 반복 처리를 멈추거나 정리하는 코드는 업무 모듈에서 작성한다.

        **반환값**

        취소를 확인했으면 True를 반환한다. 신호가 없거나 연결 오류로 확인이 지연되면 False를 반환할 수 있다.

        **사용 예**

        .. code-block:: python

            if self.FLX_IsCancel():
                self.FLX_Return_Normal(ret_msg="요청을 취소했습니다.")

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 101
             - 공통 모듈 오류
             - 비동기 실행 환경이 시작되지 않음
           * - 102
             - Async (__async_wait) 오류 (called from loop thread)
             - 비동기 실행 스레드에서 동기 대기를 호출함
           * - 103
             - Async (__async_wait) 오류: {상세 오류}
             - 비동기 처리 중 예외 또는 대기 시간 초과
           * - 201
             - Redis(async)가 전달되지 않았습니다. 스트림 기능은 Redis(async)가 필요합니다.
             - Worker에 비동기 Redis 연결이 제공되지 않음
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Scheduler_Rule(self, *, weekdays: list[int] | None = None, days: list[int] | None = None, fixed_times: list[str] | None = None, interval_hours: int | None = None, from_time: str | None = None, to_time: str | None = None) -> dict[str, Any]:
        """실행할 날짜와 시각을 검증해 스케줄 규칙을 만든다. 날짜 조건 하나와 시각 조건 하나를 선택한다.

        **인자**

        - ``weekdays`` — 요일 리스트. 일요일은 0, 토요일은 6이다.
        - ``days`` — 매월 실행할 날짜 리스트. 1~31을 사용한다.
        - ``fixed_times`` — 고정 실행 시각 리스트. 예를 들어 ["09:00", "18:00"]이다.
        - ``interval_hours`` — 반복 간격을 시간 단위의 양의 정수로 지정한다.
        - ``from_time`` — 반복 시작 시각. HH:MM 형식이다.
        - ``to_time`` — 반복 종료 시각. HH:MM 형식이며 실행 시각과 같으면 포함한다.

        **반환값**

        FLX_Scheduler_Registry() 또는 FLX_Scheduler_Next_Run_At()에 전달할 규칙 dict.

        **사용 예**

        .. code-block:: python

            rule = self.FLX_Scheduler_Rule(weekdays=[1, 3, 5], fixed_times=["09:00"])

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 331
             - weekdays 또는 days 중 하나만 지정해야 합니다.
             - 요일과 날짜를 둘 다 지정하거나 둘 다 생략함
           * - 332
             - fixed_times 또는 interval_hours 중 하나만 지정해야 합니다.
             - 고정 시각과 반복 간격을 둘 다 지정하거나 둘 다 생략함
           * - 333
             - {날짜 인자}는 {최솟값}~{최댓값} 정수의 비어 있지 않은 리스트여야 합니다.
             - 요일 또는 날짜 리스트가 비었거나 값이 범위를 벗어남
           * - 334
             - {날짜 인자}에 중복 값이 있습니다.
             - 같은 요일 또는 날짜를 여러 번 지정함
           * - 335
             - {시각 인자}은 HH:MM 형식의 00:00~23:59 시각이어야 합니다.
             - 시각 문자열의 형식 또는 범위가 잘못됨
           * - 336
             - fixed_times에는 from_time/to_time을 지정할 수 없습니다.
             - 고정 시각과 반복 구간을 함께 지정함
           * - 337
             - fixed_times는 비어 있지 않은 시각 리스트여야 합니다.
             - 고정 시각 리스트가 비었거나 리스트가 아님
           * - 338
             - fixed_times에 중복 시각이 있습니다.
             - 같은 고정 시각을 여러 번 지정함
           * - 339
             - interval_hours는 양의 정수여야 합니다.
             - 반복 간격이 양의 정수가 아님
           * - 340
             - from_time은 to_time보다 늦을 수 없습니다.
             - 반복 시작 시각이 종료 시각보다 늦음
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Scheduler_Next_Run_At(self, start_at: _datetime.datetime, stop_at: _datetime.datetime | None, rule: dict[str, Any], *, now: float | None = None) -> int | None:
        """검증한 스케줄 규칙에서 다음 실행 시각을 계산한다. 시간대가 생략된 datetime은 UTC로 해석한다.

        **인자**

        - ``start_at`` — 실행 시작 datetime.
        - ``stop_at`` — 실행 종료 datetime. None이면 종료 제한을 두지 않는다.
        - ``rule`` — FLX_Scheduler_Rule()로 만든 규칙.
        - ``now`` — 계산 기준 시각을 Unix timestamp 초 단위로 지정한다. 생략하면 현재 시각을 사용한다.

        **반환값**

        실행 가능한 최초 시각을 UTC Unix timestamp 초 단위 정수로 반환한다. 실행 시각이 없으면 None이다.

        **사용 예**

        .. code-block:: python

            from datetime import datetime, timezone

            start = datetime.now(timezone.utc)
            rule = self.FLX_Scheduler_Rule(days=[1], fixed_times=["09:00"])
            next_at = self.FLX_Scheduler_Next_Run_At(start, None, rule)
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Scheduler_Registry(self, group: str, service: str, call: str, start_at: str, stop_at: str | None, rule: dict) -> str:
        """현재 회사의 업무 실행 일정을 등록한다. 같은 그룹·서비스·업무 조합이면 기존 일정을 수정하고 cid를 유지한다.

        **인자**

        - ``group`` — 업무 그룹명.
        - ``service`` — 서비스명.
        - ``call`` — 실행할 업무 클래스 이름.
        - ``start_at`` — UTC 시작 일시 문자열. yyyy.mm.dd hh 형식이다.
        - ``stop_at`` — 같은 형식의 UTC 종료 일시. None이면 종료 제한을 두지 않는다.
        - ``rule`` — FLX_Scheduler_Rule()로 만든 실행 규칙.

        **반환값**

        등록하거나 수정한 일정의 cid 문자열.

        **사용 예**

        .. code-block:: python

            rule = self.FLX_Scheduler_Rule(weekdays=[1], fixed_times=["09:00"])
            cid = self.FLX_Scheduler_Registry("sales", "orders", "order_report", "2027.01.01 00", None, rule)

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 202
             - RedisSync가 전달되지 않았습니다.
             - Worker에 동기 Redis 연결이 제공되지 않음
           * - 331
             - weekdays 또는 days 중 하나만 지정해야 합니다.
             - 요일과 날짜를 둘 다 지정하거나 둘 다 생략함
           * - 332
             - fixed_times 또는 interval_hours 중 하나만 지정해야 합니다.
             - 고정 시각과 반복 간격을 둘 다 지정하거나 둘 다 생략함
           * - 333
             - {날짜 인자}는 {최솟값}~{최댓값} 정수의 비어 있지 않은 리스트여야 합니다.
             - 요일 또는 날짜 리스트가 비었거나 값이 범위를 벗어남
           * - 334
             - {날짜 인자}에 중복 값이 있습니다.
             - 같은 요일 또는 날짜를 여러 번 지정함
           * - 335
             - {시각 인자}은 HH:MM 형식의 00:00~23:59 시각이어야 합니다.
             - 시각 문자열의 형식 또는 범위가 잘못됨
           * - 336
             - fixed_times에는 from_time/to_time을 지정할 수 없습니다.
             - 고정 시각과 반복 구간을 함께 지정함
           * - 337
             - fixed_times는 비어 있지 않은 시각 리스트여야 합니다.
             - 고정 시각 리스트가 비었거나 리스트가 아님
           * - 338
             - fixed_times에 중복 시각이 있습니다.
             - 같은 고정 시각을 여러 번 지정함
           * - 339
             - interval_hours는 양의 정수여야 합니다.
             - 반복 간격이 양의 정수가 아님
           * - 340
             - from_time은 to_time보다 늦을 수 없습니다.
             - 반복 시작 시각이 종료 시각보다 늦음
           * - 341
             - {항목명}은 경로 구분자나 앞뒤 공백 없는 이름이어야 합니다.
             - 그룹·서비스·업무 이름의 형식이 잘못됨
           * - 342
             - {항목명}은 yyyy.mm.dd hh 형식이어야 합니다.
             - 시작 또는 종료 일시의 타입이나 표기 형식이 잘못됨
           * - 342
             - {항목명}은 유효한 yyyy.mm.dd hh 일시여야 합니다.
             - 시작 또는 종료 일시를 해석할 수 없음
           * - 343
             - stop_at은 start_at보다 빠를 수 없습니다.
             - 종료 일시가 시작보다 빠름
           * - 344
             - rule은 dict 형식이어야 합니다.
             - 규칙이 dict가 아님
           * - 344
             - rule에는 weekdays/days 중 하나와 fixed/interval 중 하나만 지정해야 합니다.
             - 규칙 키 조합이 잘못됨
           * - 344
             - fixed에 실행 시각 리스트가 필요합니다.
             - fixed 값이 None임
           * - 345
             - interval에는 every/from/to 항목이 필요합니다.
             - 반복 규칙의 타입이나 키가 잘못됨
           * - 345
             - interval.every에 시간 간격이 필요합니다.
             - 반복 간격 값이 None임
           * - 346
             - 스케줄러를 등록할 회사 코드가 없습니다.
             - 회사 코드가 없거나 형식이 잘못됨
           * - 347
             - 스케줄러 파일 저장에 실패했습니다.
             - 스케줄 파일 읽기, 검사 또는 저장 실패
           * - 348
             - 스케줄러 파일 저장 후 Redis 등록에 실패했습니다.
             - 파일 저장 뒤 Redis 등록 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Scheduler_Delete(self, group: str, service: str, call: str) -> bool:
        """현재 회사의 지정 일정을 삭제한다. 이미 큐에 들어간 업무의 취소는 별도로 처리한다.

        **인자**

        - ``group`` — 업무 그룹명.
        - ``service`` — 서비스명.
        - ``call`` — 실행할 업무 클래스 이름.

        **반환값**

        삭제에 성공했거나 해당 일정이 이미 없으면 True를 반환한다.

        **사용 예**

        .. code-block:: python

            deleted = self.FLX_Scheduler_Delete("sales", "orders", "order_report")

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 202
             - RedisSync가 전달되지 않았습니다.
             - Worker에 동기 Redis 연결이 제공되지 않음
           * - 341
             - {항목명}은 경로 구분자나 앞뒤 공백 없는 이름이어야 합니다.
             - 그룹·서비스·업무 이름의 형식이 잘못됨
           * - 346
             - 스케줄러를 삭제할 회사 코드가 없습니다.
             - 회사 코드가 없거나 형식이 잘못됨
           * - 349
             - 스케줄러 파일 삭제에 실패했습니다.
             - 스케줄 파일 읽기, 검사 또는 갱신 실패
           * - 350
             - 스케줄러 파일 처리 후 Redis 삭제에 실패했습니다.
             - 파일 처리 뒤 Redis 삭제 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_WS_Is_Stream(self) -> bool:
        """현재 요청이 WebSocket 업무인지 확인한다.

        **반환값**

        요청의 case가 "ws"이면 True를 반환한다.

        **사용 예**

        .. code-block:: python

            if self.FLX_WS_Is_Stream():
                self.FLX_WS_Start_Stream()
        """
        ...

    # --------------------------------------------------------------------
    def FLX_WS_Start_Stream(self) -> bool:
        """WebSocket 입력을 받을 준비를 한다. 업무 코드에서 입력을 직접 읽을 때 수신 함수보다 먼저 호출한다.

        **반환값**

        처음 시작하면 True, 이미 시작했으면 False를 반환한다.

        **사용 예**

        .. code-block:: python

            self.FLX_WS_Start_Stream()

        **Frontend에 전달되는 오류**

        아래 코드는 응답의 최상위 error_code와 error_msg에 기록된다. 연결과 전송 경로가 살아 있으면 Frontend에서 최종 응답을 받을 수 있다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 102
             - Async (__async_wait) 오류 (called from loop thread)
             - 비동기 실행 스레드에서 동기 대기를 호출함
           * - 103
             - Async (__async_wait) 오류: {상세 오류}
             - 비동기 처리 중 예외 또는 대기 시간 초과
           * - 104
             - 공통 모듈 오류
             - 입력 수신을 시작할 비동기 실행 환경이 준비되지 않음
           * - 203
             - WebSocket Stream 요청이 아닙니다. req_case=ws 로 요청해야 합니다.
             - 현재 요청이 WebSocket 업무가 아님
        """
        ...

    # --------------------------------------------------------------------
    def FLX_WS_Recv_Raw(self, timeout: float | None = 1.0):
        """수신을 시작한 WebSocket에서 입력 한 건을 바이트로 읽는다.

        **인자**

        - ``timeout`` — 최대 대기 시간(초). 기본값은 1초이며 None은 입력 또는 종료 신호가 올 때까지 기다린다.

        **반환값**

        수신한 bytes. 입력 종료, 취소 신호 또는 대기 시간 초과 시 None을 반환한다.

        **사용 예**

        .. code-block:: python

            self.FLX_WS_Start_Stream()
            chunk = self.FLX_WS_Recv_Raw(timeout=2.0)
        """
        ...

    # --------------------------------------------------------------------
    def FLX_WS_Recv_Text(self, timeout: float | None = 1.0, encoding: str = 'utf-8') -> str | None:
        """수신을 시작한 WebSocket에서 입력 한 건을 문자열로 읽는다.

        **인자**

        - ``timeout`` — 최대 대기 시간(초). 기본값은 1초이며 None은 입력 또는 종료 신호가 올 때까지 기다린다.
        - ``encoding`` — 바이트를 문자열로 바꿀 때 쓸 문자 인코딩. 기본값은 utf-8이다.

        **반환값**

        문자열 또는 None. 읽을 수 없는 문자는 대체 문자로 바꾼다. 인코딩 이름을 모르면 bytes의 문자열 표현을 반환한다.

        **사용 예**

        .. code-block:: python

            self.FLX_WS_Start_Stream()
            text = self.FLX_WS_Recv_Text()
        """
        ...

    # --------------------------------------------------------------------
    def FLX_WS_Recv_Json(self, timeout: float | None = 1.0, encoding: str = 'utf-8'):
        """수신을 시작한 WebSocket의 입력 한 건을 JSON으로 해석한다.

        **인자**

        - ``timeout`` — 최대 대기 시간(초). 기본값은 1초이며 None은 입력 또는 종료 신호가 올 때까지 기다린다.
        - ``encoding`` — 바이트를 문자열로 바꿀 때 쓸 문자 인코딩. 기본값은 utf-8이다.

        **반환값**

        JSON을 해석한 값. 입력 종료, 취소 신호, 대기 시간 초과 및 JSON null은 None으로 반환한다.

        **사용 예**

        .. code-block:: python

            self.FLX_WS_Start_Stream()
            message = self.FLX_WS_Recv_Json(timeout=2.0)

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 204
             - WebSocket JSON 수신 데이터 파싱 오류: {상세 오류}
             - 수신한 문자열을 JSON으로 해석하지 못함
        """
        ...

    # --------------------------------------------------------------------
    def FLX_WS_Send(self, data: Any, ret_code: int = 0, ret_msg: str = 'None') -> bool:
        """Frontend에 WebSocket 중간 응답을 보낸다. 최종 결과는 FLX_Return_Normal()로 지정한다.

        **인자**

        - ``data`` — 응답의 response_data.result에 담을 값. dict는 그대로, 문자열은 {"text": 값}으로 보낸다. UTF-8로 읽을 수 없는 bytes는 bin_b64에 담긴다. 배열을 유지하려면 {"items": 리스트}처럼 dict에 담는다.
        - ``ret_code`` — response_data.ret_code에 넣을 업무 결과 번호. 기본값은 0이다.
        - ``ret_msg`` — response_data.ret_msg에 넣을 메시지. 기본값은 문자열 "None"이다.

        **반환값**

        응답을 큐에 넣는 호출이 성공하면 True를 반환한다. 출력 큐 예외를 처리한 경우 False를 반환한다.

        **사용 예**

        .. code-block:: python

            self.FLX_WS_Send({"progress": 50}, ret_msg="처리 중")

        **Frontend에 전달되는 오류**

        아래 코드는 응답의 최상위 error_code와 error_msg에 기록된다. WebSocket 전송 경로가 살아 있으면 Frontend가 최종 응답을 받을 수 있다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 101
             - 공통 모듈 오류
             - 비동기 실행 환경이 시작되지 않음
           * - 102
             - Async (__async_wait) 오류 (called from loop thread)
             - 비동기 실행 스레드에서 동기 대기를 호출함
           * - 103
             - Async (__async_wait) 오류: {상세 오류}
             - 비동기 처리 중 예외 또는 대기 시간 초과
           * - 201
             - Redis(async)가 전달되지 않았습니다. 스트림 기능은 Redis(async)가 필요합니다.
             - Worker에 비동기 Redis 연결이 제공되지 않음
           * - 205
             - WebSocket 응답 전송은 req_case=ws_work 요청에서만 사용할 수 있습니다.
             - 현재 요청의 case가 ws가 아님
        """
        ...

    # --------------------------------------------------------------------
    def FLX_ExtLib_Stream_Run(self, case: str, name: str):
        """WebSocket 입력을 처리할 외부 라이브러리의 run_ext_api를 백그라운드에서 시작한다. 모듈 이름은 <name>_<case>이다.

        **인자**

        - ``case`` — 설치된 외부 라이브러리의 기능 구분. 예를 들어 stt이다.
        - ``name`` — 설치된 외부 라이브러리 이름.

        **반환값**

        None. 처리 결과는 FLX_ExtLib_Stream_Get_Result()로 읽는다.

        **사용 예**

        .. code-block:: python

            self.FLX_ExtLib_Stream_Run(case="stt", name="google")

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 210
             - 외부 공통 Library({모듈명}) 실행중 오류가 발생했습니다. : {상세 오류}
             - 모듈을 읽거나 백그라운드 실행을 시작하는 중 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_ExtLib_Stream_Get_Result(self):
        """외부 스트림 라이브러리가 처리한 결과 한 건을 최대 1초 기다려 읽는다.

        **반환값**

        결과 dict 또는 대기 만료 시 None. {"event": "eos"}는 입력 종료, {"event": "cancel_requested"}는 취소 신호이다.

        **사용 예**

        .. code-block:: python

            result = self.FLX_ExtLib_Stream_Get_Result()
            if result is not None and "event" not in result:
                self.FLX_WS_Send(result)
        """
        ...

    # --------------------------------------------------------------------
    def FLX_ExtLib_Simple_Run(self, case: str, name: str, req_data: dict):
        """외부 라이브러리의 run_ext_api를 호출하고 실행이 끝날 때까지 기다린다. 모듈 이름은 <name>_<case>이다.

        **인자**

        - ``case`` — 설치된 외부 라이브러리의 기능 구분. 예를 들어 mt이다.
        - ``name`` — 설치된 외부 라이브러리 이름.
        - ``req_data`` — 외부 함수에 param으로 전달할 dict.

        **반환값**

        외부 함수가 반환한 값.

        **사용 예**

        .. code-block:: python

            translated = self.FLX_ExtLib_Simple_Run("mt", "google", {"text": "안녕하세요"})

        **Frontend에 전달되는 오류**

        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.

        .. list-table::
           :header-rows: 1
           :widths: 12 50 38

           * - error_code
             - error_msg
             - 발생 조건
           * - 212
             - 외부 라이브러리 실행 중 오류가 발생했습니다.
             - 모듈 로드, 함수 조회 또는 실행 실패. 함수 누락 오류 211은 같은 cid의 Worker 로그에서 확인한다.
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_Agent_Object(self, name: str):
        """Worker에 설정된 Agent를 이름으로 가져온다.

        **인자**

        - ``name`` — 설정에 등록한 Agent 이름.

        **반환값**

        Agent 객체. 이름에 해당하는 객체가 없으면 None이다.

        **사용 예**

        .. code-block:: python

            agent = self.FLX_Get_Agent_Object("support")
            if agent is None:
                self.FLX_Return_Error(1001, "Agent 설정을 확인해 주세요.")
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Get_S3_Object(self):
        """Worker에 설정된 S3 저장소 서비스 객체를 가져온다.

        **반환값**

        S3 서비스 객체. 설정된 객체가 없으면 None이다.

        **사용 예**

        .. code-block:: python

            storage = self.FLX_Get_S3_Object()
            if storage is None:
                self.FLX_Return_Error(1001, "저장소 설정을 확인해 주세요.")
        """
        ...

    # --------------------------------------------------------------------
    def run(self) -> dict: ...

    # --------------------------------------------------------------------
    def FLX_Mongo_Get_Session(self, db_name: str = ''):
        """MongoDB 작업에 사용할 세션을 가져온다. 같은 업무에서 같은 풀 이름으로 다시 요청하면 기존 세션을 돌려준다.
    
        **인자**
    
        - ``db_name`` — Worker의 MongoDB 설정에 등록된 풀 이름. 호출할 때 이름을 지정한다. 실제 데이터베이스 이름은 조회·쓰기 함수의 database 인자에 전달한다.
    
        **반환값**
    
        조회·쓰기·집계 함수에 전달할 MongoDB 세션 객체.
    
        **사용 예**
    
        .. code-block:: python
    
            sess = self.FLX_Mongo_Get_Session("orders")
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 507
             - DB 세션을 얻을 수 없습니다.
             - 풀 이름이 비었거나 해당 풀을 찾거나 세션을 시작하는 데 실패함
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_Release_Session(self, sess) -> None:
        """MongoDB 세션을 종료하고 이 업무의 세션 목록에서 제거한다. try/finally의 finally에서 호출하면 조회나 쓰기 중 오류가 생겨도 정리를 시도할 수 있다. 세션 정리 중 잡힌 오류는 Worker 로그에서 확인한다.
    
        **인자**
    
        - ``sess`` — FLX_Mongo_Get_Session()으로 얻은 세션.
    
        **반환값**
    
        None. 다음 DB 작업에는 FLX_Mongo_Get_Session()으로 세션을 다시 얻어 사용한다.
    
        **사용 예**
    
        .. code-block:: python
    
            sess = self.FLX_Mongo_Get_Session("orders")
            try:
                orders = self.FLX_Mongo_Find(sess, "shop", "orders", limit=10)
            finally:
                self.FLX_Mongo_Release_Session(sess)
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_ObjectId(self, value: Any):
        """문자열 ID를 MongoDB의 ObjectId로 바꾼다. ObjectId로 저장된 _id를 문자열로 전달받아 조회할 때 사용한다.
    
        **인자**
    
        - ``value`` — 기존 ObjectId 또는 24자리 16진수 문자열. 문자열의 앞뒤 공백은 제거한다.
    
        **반환값**
    
        조회 조건의 _id 등에 사용할 ObjectId. 기존 ObjectId를 전달하면 그 객체를 반환한다.
    
        **사용 예**
    
        .. code-block:: python
    
            order_id = self.FLX_Mongo_ObjectId("507f1f77bcf86cd799439011")
            query_filter = {"_id": order_id}
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 508
             - bson.ObjectId 모듈을 사용할 수 없습니다.
             - Worker에서 ObjectId 변환 기능을 불러올 수 없음
           * - 509
             - Mongo ObjectId 값이 비어 있습니다.
             - 값이 None이거나 빈 문자열 또는 공백뿐임
           * - 510
             - Mongo ObjectId 형식이 올바르지 않습니다.
             - 값을 ObjectId로 변환할 수 없음
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_Find(self, sess, database: str, collection: str, query_filter: JsonDict | None = None, *, projection: JsonDict | None = None, sort: Sequence[tuple[str, int]] | None = None, limit: int = 0, skip: int = 0):
        """조건에 맞는 MongoDB 문서 여러 건을 조회한다.
    
        **인자**
    
        - ``sess`` — FLX_Mongo_Get_Session()으로 얻은 세션.
        - ``database`` — 실제 MongoDB 데이터베이스 이름.
        - ``collection`` — 대상 컬렉션 이름. 컬렉션은 문서를 모아 두는 단위이다.
        - ``query_filter`` — 문서를 찾을 조건. 예를 들어 {"status": "pending"}이다. 생략하거나 None이면 전체 문서를 대상으로 한다.
        - ``projection`` — 반환할 필드를 고른다. 예를 들어 {"status": 1, "_id": 0}이면 status를 포함하고 _id를 제외한다.
        - ``sort`` — 정렬할 필드와 방향의 목록. 1은 오름차순, -1은 내림차순이다. 예를 들어 [("created_at", -1)]이다.
        - ``limit`` — 가져올 최대 문서 수. 기본값 0은 제한 없이 가져온다.
        - ``skip`` — 앞에서 건너뛸 문서 수. 기본값은 0이다.
    
        **반환값**
    
        문서 dict의 리스트. 조건에 맞는 문서가 없으면 빈 리스트이다. 문서의 ObjectId는 문자열, 날짜와 시각은 ISO 형식의 문자열, 바이트는 16진수 문자열로 변환된다.
    
        **사용 예**
    
        .. code-block:: python
    
            sess = self.FLX_Mongo_Get_Session("orders")
            try:
                orders = self.FLX_Mongo_Find(
                    sess, "shop", "orders", {"status": "pending"},
                    sort=[("created_at", -1)], limit=10,
                )
            finally:
                self.FLX_Mongo_Release_Session(sess)
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 이미 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 511
             - Mongo Find 처리 중 오류가 발생했습니다.
             - 풀 조회, 문서 조회 또는 결과 변환 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_FindOne(self, sess, database: str, collection: str, query_filter: JsonDict | None = None, *, projection: JsonDict | None = None, sort: list[tuple[str, int]] | None = None):
        """조건에 맞는 MongoDB 문서 한 건을 조회한다. 정렬을 지정하면 정렬 순서의 첫 문서를 읽는다.
    
        **인자**
    
        - ``sess`` — FLX_Mongo_Get_Session()으로 얻은 세션.
        - ``database`` — 실제 MongoDB 데이터베이스 이름.
        - ``collection`` — 대상 컬렉션 이름. 컬렉션은 문서를 모아 두는 단위이다.
        - ``query_filter`` — 문서를 찾을 조건. 예를 들어 {"status": "pending"}이다. 생략하거나 None이면 전체 문서를 대상으로 한다.
        - ``projection`` — 반환할 필드를 고른다. 예를 들어 {"status": 1, "_id": 0}이면 status를 포함하고 _id를 제외한다.
        - ``sort`` — 정렬할 필드와 방향의 목록. 1은 오름차순, -1은 내림차순이다. 예를 들어 [("created_at", -1)]이다.
    
        **반환값**
    
        문서 dict 한 건 또는 조건에 맞는 문서가 없으면 None. 문서의 ObjectId는 문자열, 날짜와 시각은 ISO 형식의 문자열, 바이트는 16진수 문자열로 변환된다.
    
        **사용 예**
    
        .. code-block:: python
    
            order_id = self.FLX_Mongo_ObjectId("507f1f77bcf86cd799439011")
            order = self.FLX_Mongo_FindOne(sess, "shop", "orders", {"_id": order_id})
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 이미 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 512
             - Mongo FindOne 처리 중 오류가 발생했습니다.
             - 풀 조회, 단일 문서 조회 또는 결과 변환 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_Insert(self, sess, database: str, collection: str, doc: JsonDict | Sequence[JsonDict], *, ordered: bool = True):
        """MongoDB에 문서 한 건 또는 여러 건을 추가한다. 여러 건을 추가하는 중 오류가 생기면 먼저 성공한 문서가 저장되어 있을 수 있다.
    
        **인자**
    
        - ``sess`` — FLX_Mongo_Get_Session()으로 얻은 세션.
        - ``database`` — 실제 MongoDB 데이터베이스 이름.
        - ``collection`` — 대상 컬렉션 이름. 컬렉션은 문서를 모아 두는 단위이다.
        - ``doc`` — 문서 한 건은 dict, 여러 건은 dict의 리스트나 튜플로 전달한다.
        - ``ordered`` — 여러 건을 추가할 때 적용한다. 기본값 True는 순서대로 처리하다 오류가 나면 중단한다. False는 오류가 나도 다른 문서의 추가를 시도한다.
    
        **반환값**
    
        삽입 건수 inserted_count, 단건 ID inserted_id, ID 목록 inserted_ids를 담은 dict. 여러 건을 추가하면 inserted_id는 None이다.
    
        **사용 예**
    
        .. code-block:: python
    
            result = self.FLX_Mongo_Insert(
                sess, "shop", "orders", {"status": "pending", "quantity": 2},
            )
            order_id = result["inserted_id"]
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 이미 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 517
             - Mongo Insert 처리 중 오류가 발생했습니다.
             - 풀 조회, 삽입 또는 결과 확인 실패. 입력이나 결과 확인 오류 513~516은 같은 cid의 Worker 로그에서 확인한다.
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_Update(self, sess, database: str, collection: str, query_filter: JsonDict, update: JsonDict, *, many: bool = False, upsert: bool = False):
        """조건에 맞는 MongoDB 문서를 수정한다. 조건에 맞는 문서가 있어도 값이 이미 같아 실제로 수정된 문서가 없고 새로 삽입한 문서도 없으면 519 오류가 발생한다.
    
        **인자**
    
        - ``sess`` — FLX_Mongo_Get_Session()으로 얻은 세션.
        - ``database`` — 실제 MongoDB 데이터베이스 이름.
        - ``collection`` — 대상 컬렉션 이름. 컬렉션은 문서를 모아 두는 단위이다.
        - ``query_filter`` — 문서를 찾을 조건. 예를 들어 {"status": "pending"}이다.
        - ``update`` — 수정할 내용. 예를 들어 {"$set": {"status": "paid"}}이다.
        - ``many`` — 기본값 False는 한 건을 수정한다. True는 조건에 맞는 모든 문서를 수정한다.
        - ``upsert`` — True이면 조건에 맞는 문서가 없을 때 새 문서 한 건을 삽입한다. 기본값은 False이다.
    
        **반환값**
    
        조건에 맞은 수 matched_count, 실제 수정 수 modified_count, 새 문서 ID upserted_id를 담은 dict. 실제 수정 여부 updated, 새 문서 삽입 여부 inserted, 여러 건 모드 여부 many도 포함한다.
    
        **사용 예**
    
        .. code-block:: python
    
            order_id = self.FLX_Mongo_ObjectId("507f1f77bcf86cd799439011")
            result = self.FLX_Mongo_Update(
                sess, "shop", "orders", {"_id": order_id}, {"$set": {"status": "paid"}},
            )
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 이미 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 519
             - Mongo Update 처리 중 오류가 발생했습니다.
             - 풀 조회, 수정 또는 결과 확인 실패. 수정과 신규 삽입이 모두 0건이면 같은 cid의 Worker 로그에서 518을 확인한다.
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_Delete(self, sess, database: str, collection: str, query_filter: JsonDict, *, many: bool = False):
        """조건에 맞는 MongoDB 문서를 삭제한다. 삭제 조건에는 대상의 _id처럼 삭제 범위를 확인할 수 있는 값을 넣는다.
    
        **인자**
    
        - ``sess`` — FLX_Mongo_Get_Session()으로 얻은 세션.
        - ``database`` — 실제 MongoDB 데이터베이스 이름.
        - ``collection`` — 대상 컬렉션 이름. 컬렉션은 문서를 모아 두는 단위이다.
        - ``query_filter`` — 문서를 찾을 조건. 예를 들어 {"status": "pending"}이다.
        - ``many`` — 기본값 False는 한 건을 삭제한다. True는 조건에 맞는 모든 문서를 삭제한다.
    
        **반환값**
    
        삭제한 문서 수 deleted_count와 여러 건 모드 여부 many를 담은 dict. 삭제한 문서가 0건이면 521 오류가 발생한다.
    
        **사용 예**
    
        .. code-block:: python
    
            order_id = self.FLX_Mongo_ObjectId("507f1f77bcf86cd799439011")
            result = self.FLX_Mongo_Delete(sess, "shop", "orders", {"_id": order_id})
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 이미 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 521
             - Mongo Delete 처리 중 오류가 발생했습니다.
             - 풀 조회, 삭제 또는 결과 확인 실패. 삭제가 0건이면 같은 cid의 Worker 로그에서 520을 확인한다.
        """
        ...

    # --------------------------------------------------------------------
    def FLX_Mongo_Aggregate(self, sess, database: str, collection: str, pipeline: Sequence[JsonDict], *, allow_disk_use: bool = False):
        """여러 처리 단계를 순서대로 실행해 MongoDB 문서를 집계한다. 예를 들어 주문을 상태별로 나눠 건수를 계산할 때 사용한다.
    
        **인자**
    
        - ``sess`` — FLX_Mongo_Get_Session()으로 얻은 세션.
        - ``database`` — 실제 MongoDB 데이터베이스 이름.
        - ``collection`` — 대상 컬렉션 이름. 컬렉션은 문서를 모아 두는 단위이다.
        - ``pipeline`` — 처리 단계의 목록. 예를 들어 $match로 조건을 고르고 $group으로 묶어서 계산한다.
        - ``allow_disk_use`` — True이면 집계에 디스크 사용을 허용한다. 기본값은 False이다.
    
        **반환값**
    
        집계 결과 문서의 리스트. 결과가 없으면 빈 리스트이다. 문서의 ObjectId는 문자열, 날짜와 시각은 ISO 형식의 문자열, 바이트는 16진수 문자열로 변환된다.
    
        **사용 예**
    
        .. code-block:: python
    
            rows = self.FLX_Mongo_Aggregate(
                sess, "shop", "orders",
                [{"$group": {"_id": "$status", "count": {"$sum": 1}}}],
            )
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 이미 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 522
             - Mongo Aggregate 처리 중 오류가 발생했습니다.
             - 풀 조회, 집계 실행 또는 결과 변환 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_MySql_Get_Session(self, db_name: str = ''):
        """MySQL 작업을 시작할 때 사용할 세션을 가져온다. 세션은 조회나 쓰기 작업을 이어서 실행하는 데 사용한다. 같은 업무에서 같은 풀 이름으로 다시 요청하면 기존 세션을 돌려준다.
    
        **인자**
    
        - ``db_name`` — Worker의 MySQL 설정에 등록된 풀 이름. 예를 들어 orders이다. 호출할 때 이름을 지정한다.
    
        **반환값**
    
        조회, 저장, 커밋, 롤백에 전달할 MySQL 세션 객체.
    
        **사용 예**
    
        .. code-block:: python
    
            sess = self.FLX_MySql_Get_Session("orders")
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 507
             - DB 세션을 얻을 수 없습니다.
             - 풀 이름이 비어 있거나 해당 풀이 없거나 세션을 열 수 없음
        """
        ...

    # --------------------------------------------------------------------
    def FLX_MySql_Select(self, sess, query: str = '', data_set: Any = None, is_get_one: bool = False, is_scalar: bool = False):
        """세션에서 SELECT를 실행해 행 목록, 행 하나 또는 값 하나를 읽는다. 사용자 입력은 SQL에 붙이지 않고 data_set에 전달한다.
    
        **인자**
    
        - ``sess`` — FLX_MySql_Get_Session()으로 얻은 세션.
        - ``query`` — 실행할 SELECT 문.
        - ``data_set`` — SQL의 :order_id 같은 자리에 전달할 값. 예를 들어 {'order_id': 123}을 전달한다. 생략하면 전달할 값이 없는 SQL을 실행한다.
        - ``is_get_one`` — True이면 첫 행 하나를 읽는다. 기본값은 False이다.
        - ``is_scalar`` — True이면 첫 행의 첫 열 값 하나를 읽는다. is_get_one보다 우선하며 기본값은 False이다.
    
        **반환값**
    
        기본값은 행 dict의 리스트이며 조회 결과가 없으면 빈 리스트이다. is_get_one=True이면 첫 행 dict 또는 빈 dict를 반환한다. is_scalar=True이면 값 하나 또는 None을 반환한다.
    
        **사용 예**
    
        .. code-block:: python
    
            sess = self.FLX_MySql_Get_Session("orders")
            try:
                order = self.FLX_MySql_Select(
                    sess, "SELECT id, status FROM orders WHERE id = :order_id",
                    data_set={"order_id": 123}, is_get_one=True,
                )
            finally:
                self.FLX_MySql_Release_Session(sess)
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 531
             - DB Select 처리 중 오류가 발생했습니다.
             - 풀을 조회하거나 SELECT를 실행하고 결과를 읽는 중 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_MySql_Execute(self, sess, query: str = '', data_set: Any = None, is_get_last_id: bool = False):
        """세션에서 INSERT, UPDATE, DELETE 같은 쓰기 SQL을 실행한다. 저장을 확정하려면 같은 세션에서 FLX_MySql_Commit()을 호출한다.
    
        **인자**
    
        - ``sess`` — FLX_MySql_Get_Session()으로 얻은 세션.
        - ``query`` — 실행할 SQL 문.
        - ``data_set`` — SQL의 :order_id 같은 자리에 전달할 값. 예를 들어 {'order_id': 123}을 전달한다. 생략하면 전달할 값이 없는 SQL을 실행한다.
        - ``is_get_last_id`` — True이면 같은 연결에서 LAST_INSERT_ID()를 읽는다. 자동 증가 ID를 만든 INSERT 뒤에 사용한다. 기본값은 False이다.
    
        **반환값**
    
        기본값은 빈 dict이다. is_get_last_id=True이면 {'last_id': 값}을 반환한다.
    
        **사용 예**
    
        .. code-block:: python
    
            sess = self.FLX_MySql_Get_Session("orders")
            try:
                result = self.FLX_MySql_Execute(
                    sess, "INSERT INTO orders (status) VALUES (:status)",
                    data_set={"status": "pending"}, is_get_last_id=True,
                )
                self.FLX_MySql_Commit(sess)
            finally:
                self.FLX_MySql_Release_Session(sess)
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 532
             - DB Execute 처리 중 오류가 발생했습니다.
             - 풀 조회, SQL 실행 또는 마지막 삽입 ID 조회 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_MySql_Commit(self, sess) -> None:
        """현재 세션에서 실행한 쓰기 작업을 DB에 확정한다. 여러 SQL을 한 작업으로 처리할 때는 필요한 SQL을 모두 실행한 뒤 호출한다.
    
        **인자**
    
        - ``sess`` — FLX_MySql_Get_Session()으로 얻은 세션.
    
        **반환값**
    
        None.
    
        **사용 예**
    
        .. code-block:: python
    
            self.FLX_MySql_Commit(sess)
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 533
             - DB Commit 처리 중 오류가 발생했습니다.
             - 풀 조회 또는 변경사항 확정 중 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_MySql_Rollback(self, sess) -> None:
        """현재 세션에서 아직 확정하지 않은 변경사항을 취소한다. 예를 들어 후속 검증이 실패해 앞에서 실행한 SQL을 되돌릴 때 사용한다.
    
        **인자**
    
        - ``sess`` — FLX_MySql_Get_Session()으로 얻은 세션.
    
        **반환값**
    
        None.
    
        **사용 예**
    
        .. code-block:: python
    
            if invalid_order:
                self.FLX_MySql_Rollback(sess)
                self.FLX_Return_Error(1001, "주문 정보를 확인해 주세요.")
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 506
             - 등록되지 않은 DB 세션입니다. (이미 반환되었거나 다른 세션 객체입니다)
             - 반환한 세션이나 이 업무에 등록되지 않은 세션을 사용함
           * - 534
             - DB Rollback 처리 중 오류가 발생했습니다.
             - 풀 조회 또는 변경사항 취소 중 실패
        """
        ...

    # --------------------------------------------------------------------
    def FLX_MySql_Release_Session(self, sess) -> None:
        """MySQL 세션을 닫고 이 업무에서 사용한 세션 목록에서 제거한다. try/finally의 finally에서 호출하면 업무 처리 중 예외가 생겨도 세션을 정리할 수 있다. 쓰기 결과를 저장하려면 반환 전에 커밋한다.
    
        **인자**
    
        - ``sess`` — FLX_MySql_Get_Session()으로 얻은 세션.
    
        **반환값**
    
        None. 이후 DB 작업에는 FLX_MySql_Get_Session()으로 세션을 다시 얻어 사용한다.
    
        **사용 예**
    
        .. code-block:: python
    
            sess = self.FLX_MySql_Get_Session("orders")
            try:
                count = self.FLX_MySql_Select(sess, "SELECT COUNT(*) FROM orders", is_scalar=True)
            finally:
                self.FLX_MySql_Release_Session(sess)
    
        **Frontend에 전달되는 오류**
    
        응답의 최상위 error_code와 error_msg에 아래 값이 담긴다. 중괄호에는 실제 값이 들어간다.
    
        .. list-table::
           :header-rows: 1
           :widths: 12 50 38
    
           * - error_code
             - error_msg
             - 발생 조건
           * - 502
             - DBPool이 존재하지 않거나 형식이 dict가 아닙니다.
             - 등록된 세션의 풀 목록이 없거나 dict가 아님
           * - 504
             - {풀 이름}에 대한 DBPool이 존재하지 않습니다.
             - 등록된 세션에 해당하는 풀이 없음
           * - 505
             - {풀 이름}에 대한 Pool이 존재하지 않습니다.
             - 해당 이름의 풀이 MySQLPool 타입이 아님
        """
        ...
