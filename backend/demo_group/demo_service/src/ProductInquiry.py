"""
최초: 2026.10.26
내용: Live Fluxon 개발 체험용 상품 조회. 실제 MySQL에서 기본 조회와 가격 오름차순 정렬을 수행한다.
"""
import re
from work_lib import *


class ProductInquiry(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # null 허용 및 엄격한 타입/범위 검사는 아래에서 업무 코드로 반환한다.
        for field in ("category", "limit", "sort"):
            self.FLX_Check_Request_Data(field, is_exist=False)

    def FLX_Main_Work_Start(self):
        data = self.FLX_Get_Request_Data()
        category = data.get("category")
        limit = data.get("limit", 50)
        sort = data.get("sort", "id")
        if category is not None and not isinstance(category, str):
            return self.FLX_Return_Normal(ret_code=10, ret_msg="입력값의 타입을 확인하세요.")
        if type(limit) is not int:
            return self.FLX_Return_Normal(ret_code=10, ret_msg="입력값의 타입을 확인하세요.")
        if not isinstance(sort, str):
            return self.FLX_Return_Normal(ret_code=10, ret_msg="입력값의 타입을 확인하세요.")

        if category is not None and not re.fullmatch(r"[A-Z_]{1,40}", category):
            return self.FLX_Return_Normal(ret_code=11, ret_msg="입력값의 범위나 형식을 확인하세요.")
        if not 1 <= limit <= 50:
            return self.FLX_Return_Normal(ret_code=11, ret_msg="입력값의 범위나 형식을 확인하세요.")
        if sort not in ("id", "price_asc"):
            return self.FLX_Return_Normal(ret_code=11, ret_msg="입력값의 범위나 형식을 확인하세요.")

        schema_name = self.FLX_Get_Property_Default_StorageName
        db_session = self.FLX_MySql_Get_Session("MySQL")
        try:
            replacements = {"{schema_name}": schema_name}
            count_sql = self.FLX_Query_Load(0, replacements)
            rows_sql = self.FLX_Query_Load(2 if sort == "price_asc" else 1, replacements)
            if not count_sql or not rows_sql:
                return self.FLX_Return_Normal(ret_code=12, ret_msg="상품 조회 설정 또는 DB 결과를 확인할 수 없습니다.")
            params = {"category": category, "limit": limit}
            count = self.FLX_MySql_Select(db_session, count_sql, {"category": category}, is_get_one=True)
            rows = self.FLX_MySql_Select(db_session, rows_sql, params)
            if not isinstance(count, dict) or type(count.get("total")) is not int or not isinstance(rows, list):
                return self.FLX_Return_Normal(ret_code=12, ret_msg="상품 조회 설정 또는 DB 결과를 확인할 수 없습니다.")
            result = {"items": rows, "total": count["total"]}
        finally:
            try:
                self.FLX_MySql_Rollback(db_session)
            finally:
                self.FLX_MySql_Release_Session(db_session)
        return self.FLX_Return_Normal(_return=result, ret_code=0, ret_msg="상품을 조회했습니다.")
