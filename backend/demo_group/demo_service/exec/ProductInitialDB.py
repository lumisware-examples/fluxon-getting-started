"""
최초: 2026.11.10
내용: AUTO_INCREMENT 유무만 확인해 null 또는 "reset"을 반환합니다.
"""
from work_lib import *


class ProductInitialDB(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        try:
            schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)
            query = self.FLX_Query_Load(query_num=0)
            column = self.FLX_MySql_Select(db_session, query, {"schema_name": schema_name}, is_scalar=True)
            result = None if column == "auto_increment" else "reset"
        finally:
            try:
                self.FLX_MySql_Rollback(db_session)
            finally:
                self.FLX_MySql_Release_Session(db_session)

        # 테이블 변경은 프런트엔드가 호출하는 ProductReset이 담당합니다.
        self.FLX_Return_Normal(_return=result, ret_code=0)
