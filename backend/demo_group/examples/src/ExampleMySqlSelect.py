"""07. 목록·단건·스칼라 조회를 비교합니다."""
from work_lib import *


class ExampleMySqlSelect(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)
        
    def FLX_Main_Field_Check(self):
        self.FLX_Check_Request_Data("id", is_exist=False)
        self.FLX_Check_Request_Data("limit", is_exist=False)

    def FLX_Main_Work_Start(self):
        data = self.FLX_Get_Request_Data()
        item_id, limit = data.get("id", 1), data.get("limit", 10)
        if not self.FLX_Call_Common_Func("examples_common", "valid_id", item_id):
            self.FLX_Return_Normal(ret_code=10, ret_msg="ID는 1–2147483647의 정수로 입력하세요.")
        if type(limit) is not int or not 1 <= limit <= 50:
            self.FLX_Return_Normal(ret_code=11, ret_msg="조회 개수는 1–50의 정수로 입력하세요.")

        if True:
            # svc_common 디렉토리에 저장된 공통 함수 호출 - 파일명: flx_work_com, 함수명: get_mysql_context
            schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)
        else:
            # 별도 svc_info에 환경 변수가 있는 경우
            mysql_info = self.FLX_Get_Info_Read("mysql.json")
            schema_name = mysql_info["schema_name"]
            db_session = self.FLX_MySql_Get_Session(mysql_info["db_name"])

        try:
            replacements = {"{schema_name}": schema_name}
            list_sql = self.FLX_Query_Load(0, replacements)
            limit_sql = self.FLX_Query_Load(1, replacements)
            one_sql = self.FLX_Query_Load(2, replacements)
            count_sql = self.FLX_Query_Load(3, replacements)

            all_items = self.FLX_MySql_Select(db_session, list_sql)
            self.FLX_LOG(DEBUG, f"테이블 데이터 전체 조회 결과: {type(all_items)}\n {all_items}")

            items = self.FLX_MySql_Select(db_session, limit_sql, {"limit": limit})
            self.FLX_LOG(DEBUG, f"테이블 데이터 limit 조회 결과: {type(items)}\n {items}")

            item = self.FLX_MySql_Select(db_session, one_sql, {"id": item_id}, is_get_one=True)
            self.FLX_LOG(DEBUG, f"테이블 데이터 1개 조회 결과: {type(item)}\n {item}")

            total = self.FLX_MySql_Select(db_session, count_sql, is_scalar=True)
            self.FLX_LOG(DEBUG, f"테이블 조건 요청한 category인 데이터 갯수 조회 결과: {type(total)}\n {total}")
        finally:
            # 읽기 트랜잭션도 정리합니다. rollback 실패 시에도 세션을 반환합니다.
            try:
                self.FLX_MySql_Rollback(db_session)
            finally:
                self.FLX_MySql_Release_Session(db_session)

        # 단건이 없으면 빈 dict, 목록이 없으면 빈 list입니다. 빈 결과도 정상입니다.
        response = {"all_items": all_items, "items": items, "item": item, "total": total}
        self.FLX_Return_Normal(_return=response, ret_msg="실습 데이터를 조회했습니다.")
