"""
최초: 2026.10.26
내용: MySQL에서 Update 예제
History
  2026.11.10: 입력 검사와 예외 시 rollback 및 세션 반환을 보완.
  2026.11.09: DB 접근 전에 공통 상품 입력 검증을 수행.
"""
from work_lib import * #type: ignore


class ExampleUpdate(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # 변수 필수 체크
        self.FLX_Check_Request_Data("id", is_exist=False)
        # 타입을 자동 변환하지 않습니다. 누락·타입·범위 오류는 공통 검증에서 ret_code로 반환합니다.
        for field in ("name", "category", "price"):
            self.FLX_Check_Request_Data(field, is_exist=False)

    def FLX_Main_Work_Start(self):
        # 프런트엔드를 거치지 않는 요청도 같은 규칙으로 검사합니다.
        product_id, ret_code, ret_msg = self.FLX_Call_Common_Func(
            "flx_work_com", "validate_product_id", self.FLX_Get_Request_Data().get("id")
        )
        if ret_code != 0:
            self.FLX_Return_Normal(ret_code=ret_code, ret_msg=ret_msg)
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
            # 요청한 ID의 상품이 있는지 확인합니다.
            product_query = self.FLX_Query_Load(query_num=0, replace_items={"{schema_name}": schema_name})
            product_count = self.FLX_MySql_Select(db_session, product_query, {"id": product_id}, is_scalar=True)

            if product_count > 0:
                # products 테이블 수정할 데이터
                payload = {
                    "id": product_id,
                    "category": category,
                    "name": name,
                    "price": price
                }
                # products 테이블 수정 쿼리(정상 쿼리)
                product_update_query = self.FLX_Query_Load(query_num=1, replace_items={"{schema_name}": schema_name})
                self.FLX_MySql_Execute(db_session, product_update_query, payload)

                # 변경한 내용을 DB에 확정합니다(commit).
                self.FLX_MySql_Commit(db_session)
            else:
                self.FLX_MySql_Rollback(db_session)
                self.FLX_Return_Error(ret_code=10, ret_msg="수정할 상품이 없습니다.")
        except Exception:
            self.FLX_MySql_Rollback(db_session)
            self.FLX_Return_Error(ret_code=10, ret_msg="수정할 상품이 없습니다.")

        # msg/ExampleUpdate_msg.json의 c_code, ret_code 키 값을 매핑된 메시지가 전달, 매핑될 데이터가 없는 경우 ret_msg 값이 전달
        self.FLX_Return_Normal(_return={"id": product_id}, ret_code=0, ret_msg="상품 수정이 완료되었습니다.")
