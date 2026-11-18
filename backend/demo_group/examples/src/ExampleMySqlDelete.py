"""10. 다른 모듈의 SQL을 재사용해 대상을 확인하고 삭제합니다."""
from work_lib import *


class ExampleMySqlDelete(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        self.FLX_Check_Request_Data("id")

    def FLX_Main_Work_Start(self):
        item_id = self.FLX_Get_Request_Data("id")
        # 공통 함수를 이용하여 전달된 id가 정수인지 확인합니다.
        if not self.FLX_Call_Common_Func("examples_common", "valid_id", item_id):
            self.FLX_Return_Error(ret_code=11, ret_msg="ID는 1–2147483647의 정수로 입력하세요.")

        schema_name, session = self.FLX_Call_Common_Func("examples_common", "get_mysql_context", self)
        try:
            replacements = {"{schema_name}": schema_name}
            # 같은 examples 서비스에 있는 Update의 행 잠금 SQL을 재사용합니다.
            select_sql = self.FLX_Other_Query_Load("ExampleMySqlUpdate", 0, replace_items=replacements)
            delete_sql = self.FLX_Query_Load(0, replacements)
            if not select_sql or not delete_sql:
                # ExampleMySqlDelete_msg.json 에서 대응할 수 없는 ret_code에 대해서는 직접 입력한 ret_msg가 전달 됩니다.
                self.FLX_Return_Error(ret_code=99, ret_msg="삭제 SQL과 ExampleMySqlUpdate_0.sql을 반영하세요.")
            found = self.FLX_MySql_Select(session, select_sql, {"id": item_id}, is_get_one=True)
            if found:
                self.FLX_MySql_Execute(session, delete_sql, {"id": item_id})
                self.FLX_MySql_Commit(session)
            else:
                self.FLX_MySql_Rollback(session)
                self.FLX_Return_Normal(ret_code=10, ret_msg="삭제할 실습 데이터가 없습니다.")
        except Exception:
            self.FLX_MySql_Rollback(session)
            self.FLX_Return_Error(ret_code=12, ret_msg="에러가 발생하였습니다.")
        finally:
            # mysql session 해제 - 필요 시 직접 수행이 가능합니다.(선택사항)
            self.FLX_MySql_Release_Session(session)

        self.FLX_Return_Normal(_return={"id": item_id}, ret_msg="실습 데이터를 삭제했습니다.")
