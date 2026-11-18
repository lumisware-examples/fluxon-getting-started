"""11. 같은 세션의 INSERT 두 개를 함께 확정하거나 함께 취소합니다."""
from work_lib import *

class ExampleTransaction(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        simulate_failure = self.FLX_Get_Request_Data().get("simulate_failure", False)
        if type(simulate_failure) is not bool:
            self.FLX_Return_Normal(ret_code=11, ret_msg="simulate_failure는 true 또는 false로 입력하세요.")

        request_key = self.FLX_Get_UUID()
        schema_name, session = self.FLX_Call_Common_Func("examples_common", "get_mysql_context", self)
        item_ids = []

        try:
            sql = self.FLX_Query_Load(0, {"{schema_name}": schema_name})
            for number in (1, 2):
                values = {"name": f"거래 실습 {request_key}-{number}", "price": number * 1000}
                inserted = self.FLX_MySql_Execute(session, sql, values, is_get_last_id=True)
                item_id = inserted.get("last_id") if isinstance(inserted, dict) else None
                item_ids.append(item_id)
            if simulate_failure:
                # 두 INSERT가 실행됐어도 commit 전이면 함께 되돌릴 수 있습니다.
                self.FLX_MySql_Rollback(session)
                self.FLX_Return_Error(ret_code=10, ret_msg="실습 실패를 재현해 두 등록을 모두 취소했습니다.")

            self.FLX_MySql_Commit(session)
        except Exception:
            self.FLX_MySql_Rollback(session)
            self.FLX_Return_Error(ret_code=10, ret_msg="실습 실패를 재현해 두 등록을 모두 취소했습니다.")

        # rollback된 ID를 저장된 데이터의 ID처럼 돌려주지 않습니다.
        result = {"committed": simulate_failure, "ids": item_ids if simulate_failure else [], "request_key": request_key}

        self.FLX_Return_Normal(_return=result, ret_msg="두 등록을 하나의 트랜잭션으로 확정했습니다.")
