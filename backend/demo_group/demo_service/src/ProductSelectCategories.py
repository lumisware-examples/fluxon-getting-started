"""
최초: 2026.10.26
내용: MySQL에 저장된 상품 종류를 중복 없이 조회한다.
"""
import time
from work_lib import * #type: ignore


class ProductSelectCategories(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # 아래 코드 블록은  request_data에서 필수 파라미터 오지 않았을 때의 에러 확인용 코드
        if False:
            self.FLX_Check_Request_Data("category", str)
        # 상품 종류 전체를 조회하므로 필수 입력값이 없습니다.
        pass

    def FLX_Main_Work_Start(self):
        schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)

        # 조회만 수행했더라도 세션은 반드시 반환합니다.
        try:
            # 아래 코드 블록은 결과가 wait_sec보다 늦게 오는 폴링 지연 실습
            if False:
                time.sleep(5)
            categories_query = self.FLX_Query_Load(query_num=0, replace_items={"{schema_name}": schema_name})
            rows = self.FLX_MySql_Select(db_session, categories_query)
        finally:
            try:
                self.FLX_MySql_Rollback(db_session)
            finally:
                self.FLX_MySql_Release_Session(db_session)

        if not isinstance(rows, list) or any(
                not isinstance(row, dict) or not isinstance(row.get("category"), str) for row in rows):
            self.FLX_Return_Normal(ret_code=12, ret_msg="상품 종류 조회 결과를 확인할 수 없습니다.")

        categories = [row["category"] for row in rows]
        self.FLX_Return_Normal(_return={"categories": categories}, ret_code=0)
