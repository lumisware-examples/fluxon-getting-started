"""
최초: 2026.10.26
내용: MySQL에서 Insert 예제
History
  2026.11.10: AUTO_INCREMENT로 채번하고 INSERT 결과의 last_id를 반환.
  2026.11.10: 입력 검사와 예외 시 rollback 및 세션 반환을 보완.
  2026.11.09: DB 접근 전에 공통 상품 입력 검증을 수행.
"""
from work_lib import * #type: ignore


class ExampleInsert(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # 변수 필수 체크
        # 타입을 자동 변환하지 않습니다. 누락·타입·범위 오류는 공통 검증에서 ret_code로 반환합니다.
        for field in ("name", "category", "price"):
            self.FLX_Check_Request_Data(field, is_exist=False)

    def FLX_Main_Work_Start(self):
        # 검증 실패는 여기서 작업을 종료하므로, DB 조회·변경·commit이 실행되지 않습니다.
        values, ret_code, ret_msg = self.FLX_Call_Common_Func("flx_work_com", "validate_product_values", self.FLX_Get_Request_Data())
        if ret_code != 0:
            self.FLX_Return_Normal(ret_code=ret_code, ret_msg=ret_msg)
        category = values["category"]
        name = values["name"]
        price = values["price"]

        # svc_common 디렉토리에 저장된 공통 함수 호출 - 파일명: flx_work_com, 함수명: get_mysql_context
        schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)

        # SQL 실행 중 예외가 발생하면 변경을 취소하고, 성공/실패 모두 세션을 반환합니다.
        try:
            # id는 보내지 않습니다. DB가 같은 테이블의 동시 등록 요청마다 고유 ID를 발급합니다.
            payload = {"category": category, "name": name, "price": price}
            product_insert_query = self.FLX_Query_Load(query_num=0, replace_items={"{schema_name}": schema_name})
            inserted = self.FLX_MySql_Execute(db_session, product_insert_query, payload, is_get_last_id=True)
            # 다른 세션에서 MAX(id)를 조회하면 다른 요청의 ID를 받을 수 있으므로 사용하지 않습니다.
            product_id = inserted.get("last_id") if isinstance(inserted, dict) else None
            valid_id = type(product_id) is int and 1 <= product_id <= 2147483647

            if valid_id:
                self.FLX_MySql_Commit(db_session)
            else:
                # INSERT 결과를 확인하지 못하면 저장을 취소하고 성공으로 표시하지 않습니다.
                self.FLX_MySql_Rollback(db_session)
                self.FLX_Return_Error(ret_code=19, ret_msg="DB가 발급한 상품 ID를 확인할 수 없습니다.")
        except Exception:
            self.FLX_MySql_Rollback(db_session)
            self.FLX_Return_Error(ret_code=19, ret_msg="DB가 발급한 상품 ID를 확인할 수 없습니다.")

        # msg/ExampleInsert_msg.json의 c_code, ret_code 키 값을 매핑된 메시지가 전달, 매핑될 데이터가 없는 경우 ret_msg 값이 전달
        self.FLX_Return_Normal(_return={"id": product_id}, ret_code=0, ret_msg="등록이 완료되었습니다.")
