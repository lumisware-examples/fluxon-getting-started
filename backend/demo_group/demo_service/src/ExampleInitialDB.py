"""
최초: 2026.11.10
내용: AUTO_INCREMENT 유무만 확인해 null 또는 "reset"을 반환합니다.
History
  2026.11.10: 프런트엔드 초기화 분기와 설명을 맞추고 조회 세션 정리를 보완.
"""
from work_lib import *


class ExampleInitialDB(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        if True:
            # svc_common 디렉토리에 저장된 공통 함수 호출 - 파일명: flx_work_com, 함수명: get_mysql_context
            schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)
        else:
            # 별도 svc_info에 환경 변수가 있는 경우
            mysql_info = self.FLX_Get_Info_Read("mysql.json")
            schema_name = mysql_info["schema_name"]
            db_session = self.FLX_MySql_Get_Session(mysql_info["db_name"])

        try:
            query = self.FLX_Query_Load(query_num=0)
            column = self.FLX_MySql_Select(db_session, query, {"schema_name": schema_name}, is_scalar=True)
            result = None if column == "auto_increment" else "reset"
        finally:
            try:
                self.FLX_MySql_Rollback(db_session)
            finally:
                self.FLX_MySql_Release_Session(db_session)

        # 테이블 변경은 프런트엔드가 호출하는 ExampleReset이 담당합니다.
        self.FLX_Return_Normal(_return=result, ret_code=0)
