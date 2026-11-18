"""
최초: 2026.10.26
내용: 상품 체험 준비와 초기화. 테이블을 다시 만들고 예제 상품 5개를 등록합니다.
History
  2026.11.10: 준비 모듈을 통합하고 AUTO_INCREMENT 테이블 재생성으로 변경.
"""
from work_lib import * #type: ignore


class ExampleReset(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)
        try:
            replacements = {"{schema_name}": schema_name}
            # 삭제 전에 SQL 3개를 모두 읽습니다. 파일이 빠졌으면 기존 테이블을 건드리지 않습니다.
            drop_sql = self.FLX_Query_Load(query_num=0, replace_items=replacements)
            create_sql = self.FLX_Query_Load(query_num=1, replace_items=replacements)
            seed_sql = self.FLX_Query_Load(query_num=2, replace_items=replacements)
            ready = bool(drop_sql and create_sql and seed_sql)
            if ready:
                # 기존 데이터와 ID 채번 상태를 버리고 테이블 구조까지 다시 준비합니다.
                # MySQL의 DROP/CREATE는 암시적으로 commit되므로 rollback으로 복구되지 않습니다.
                self.FLX_MySql_Execute(db_session, drop_sql)
                self.FLX_MySql_Execute(db_session, create_sql)
                self.FLX_MySql_Execute(db_session, seed_sql)
                # 예제 상품 INSERT를 확정한 뒤에만 성공을 반환합니다.
                self.FLX_MySql_Commit(db_session)
            else:
                self.FLX_MySql_Rollback(db_session)
                self.FLX_Return_Error(ret_code=12, ret_msg="상품 초기화 SQL을 확인할 수 없습니다.")
        except Exception:
            # 아직 확정되지 않은 INSERT만 취소합니다. 삭제한 기존 테이블은 돌아오지 않습니다.
            self.FLX_MySql_Rollback(db_session)
            self.FLX_Return_Error(ret_code=12, ret_msg="상품 초기화 SQL을 확인할 수 없습니다.")

        self.FLX_Return_Normal(ret_code=0, ret_msg="상품 테이블을 다시 만들고 예제 상품 5개를 등록했습니다.")
