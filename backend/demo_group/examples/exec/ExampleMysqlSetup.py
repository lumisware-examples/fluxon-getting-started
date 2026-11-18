"""MySQL 실습 전에 전용 테이블을 준비합니다. 기존 데이터는 유지합니다."""

from work_lib import *


class ExampleMysqlSetup(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        # 그룹 공통 함수로 DB 연결을 얻습니다. SQL의 스키마는 워커 기본 저장소입니다.
        schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)

        try:
            query = self.FLX_Query_Load(0, {"{schema_name}": schema_name})

            # CREATE IF NOT EXISTS이므로 반복 실행해도 기존 행과 ID를 유지합니다.
            # MySQL DDL은 암시적으로 commit됩니다. rollback으로 생성 전 상태로 돌아가지는 않습니다.
            self.FLX_MySql_Execute(db_session, query)
            self.FLX_MySql_Commit(db_session)
        except Exception:
            self.FLX_MySql_Rollback(db_session)
            self.FLX_Return_Error(_return={"table": "getting_started_example_items"}, ret_code=10, ret_msg="실습 테이블 생성을 실패하였습니다.")
        finally:
            self.FLX_MySql_Release_Session(db_session)

        # 응답으로 작업을 끝내기 전에 세션 정리를 마칩니다.
        self.FLX_Return_Normal(_return={"table": "getting_started_example_items"}, ret_code=0, ret_msg="실습 테이블 준비를 완료했습니다.")
