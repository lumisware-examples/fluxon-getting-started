"""09. 행을 잠가 대상을 확인한 뒤 수정합니다."""
from work_lib import *


class ExampleMySqlUpdate(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        self.FLX_Check_Request_Data("id")

    def FLX_Main_Work_Start(self):
        data = self.FLX_Get_Request_Data()
        item_id = self.FLX_Get_Request_Data("id")
        if not self.FLX_Call_Common_Func("examples_common", "valid_id", item_id):
            self.FLX_Return_Normal(ret_code=13, ret_msg="ID는 1–2147483647의 정수로 입력하세요.")
        values, code, message = self.FLX_Call_Common_Func("examples_common", "validate_item", data)
        if code != 0:
            self.FLX_Return_Normal(ret_code=code, ret_msg=message)

        schema_name, session = self.FLX_Call_Common_Func("examples_common", "get_mysql_context", self)
        try:
            replacements = {"{schema_name}": schema_name}
            select_sql = self.FLX_Query_Load(0, replacements)
            update_sql = self.FLX_Query_Load(1, replacements)

            # FOR UPDATE 잠금은 commit/rollback까지 유지됩니다. 실습 테이블은 InnoDB입니다.
            found = self.FLX_MySql_Select(session, select_sql, {"id": item_id}, is_get_one=True)
            if found:
                self.FLX_MySql_Execute(session, update_sql, {**values, "id": item_id})
                self.FLX_MySql_Commit(session)
            else:
                self.FLX_MySql_Rollback(session)
        except Exception:
            self.FLX_MySql_Rollback(session)
            self.FLX_Return_Error(ret_code=10, ret_msg="수정할 실습 데이터가 없습니다.")

        self.FLX_Return_Normal(_return={"id": item_id}, ret_msg="실습 데이터를 수정했습니다.")
