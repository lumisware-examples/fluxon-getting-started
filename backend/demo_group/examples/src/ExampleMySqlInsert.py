"""08. ID를 생략해 등록하고 같은 연결의 last_id를 반환합니다."""
from work_lib import *


class ExampleMySqlInsert(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        data = self.FLX_Get_Request_Data()
        # request_data 의 name, price 값의 정상 범위를 확인합니다
        values, code, message = self.FLX_Call_Common_Func("examples_common", "validate_item", data)

        if code != 0:
            self.FLX_Return_Error(ret_code=code, ret_msg=message)

        schema_name, session = self.FLX_Call_Common_Func("examples_common", "get_mysql_context", self)
        try:
            sql = self.FLX_Query_Load(0, {"{schema_name}": schema_name})
            inserted = self.FLX_MySql_Execute(session, sql, values, is_get_last_id=True)
            item_id = inserted.get("last_id") if isinstance(inserted, dict) else None

            self.FLX_LOG(DEBUG, f"insert 결과 확인 : item_id = {item_id}")

            if item_id:
                self.FLX_MySql_Commit(session)
            else:
                self.FLX_MySql_Rollback(session)

        except Exception:
            self.FLX_MySql_Rollback(session)

        # 반환 API는 즉시 작업을 끝내므로 commit·세션 정리를 마친 뒤 호출합니다.
        self.FLX_Return_Normal(_return={"id": item_id}, ret_msg="실습 데이터를 등록했습니다.")
