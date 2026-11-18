"""
최초: 2026.10.26
내용: MySQL에서 Delete 예제
"""
from work_lib import * #type: ignore


class ExampleDelete(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # 변수 필수 체크
        self.FLX_Check_Request_Data("id", is_exist=False)

    def FLX_Main_Work_Start(self):
        # 프런트엔드를 거치지 않는 요청도 같은 규칙으로 검사합니다.
        product_id, ret_code, ret_msg = self.FLX_Call_Common_Func(
            "flx_work_com", "validate_product_id", self.FLX_Get_Request_Data().get("id")
        )
        if ret_code != 0:
            self.FLX_Return_Normal(ret_code=ret_code, ret_msg=ret_msg)

        # svc_common 디렉토리에 저장된 공통 함수 호출 - 파일명: flx_work_com, 함수명: get_mysql_context
        schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)

        # SQL 실행 중 예외가 발생하면 변경을 취소하고, 성공/실패 모두 세션을 반환합니다.
        try:
            # 다른 모듈의 SQL을 재사용하는 예제: ExampleUpdate_0.sql로 존재 여부를 확인합니다.
            product_query = self.FLX_Other_Query_Load(req_name="ExampleUpdate", query_num=0, replace_items={"{schema_name}": schema_name})
            product_count = self.FLX_MySql_Select(db_session, product_query, {"id": product_id}, is_scalar=True)

            self.FLX_LOG(DEBUG, f"product_count = {product_count}")

            if product_count > 0:
                # products 테이블 삭제할 데이터
                payload = {
                    "id": product_id
                }
                # products 테이블 삭제 쿼리(정상 쿼리)
                product_delete_query = self.FLX_Query_Load(query_num=0, replace_items={"{schema_name}": schema_name})
                self.FLX_MySql_Execute(db_session, product_delete_query, payload)

                # 변경한 내용을 DB에 확정합니다(commit).
                self.FLX_MySql_Commit(db_session)
            else:
                self.FLX_MySql_Rollback(db_session)
                self.FLX_Return_Error(ret_code=10, ret_msg="삭제할 상품이 없습니다.")
        except Exception:
            self.FLX_MySql_Rollback(db_session)
            self.FLX_Return_Error(ret_code=10, ret_msg="삭제할 상품이 없습니다.")

        # msg/ExampleDelete_msg.json의 c_code, ret_code 키 값을 매핑된 메시지가 전달, 매핑될 데이터가 없는 경우 ret_msg 값이 전달
        self.FLX_Return_Normal(_return={"id": product_id}, ret_code=0, ret_msg="상품 삭제가 완료되었습니다.")
