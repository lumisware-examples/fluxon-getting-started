"""
최초: 2026.10.26
내용: MySQL에서 Select 예제
History
  2026.11.10: 조회 세션 정리와 학습 주석을 보완.
"""
from work_lib import * #type: ignore

class ExampleSelect(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # category 변수 필수 체크
        self.FLX_Check_Request_Data("category", str)

    def FLX_Main_Work_Start(self):
        data = self.FLX_Get_Request_Data()

        # svc_common 디렉토리에 저장된 공통 함수 호출 - 파일명: flx_work_com, 함수명: get_mysql_context
        schema_name, db_session = self.FLX_Call_Common_Func("flx_work_com", "get_mysql_context", self)

        # 조회만 수행했더라도 세션은 반드시 반환합니다.
        try:
            category = data["category"]

            # products 테이블 데이터 전체 조회
            all_products_query = self.FLX_Query_Load(query_num=0, replace_items={"{schema_name}": schema_name})
            products = self.FLX_MySql_Select(db_session, all_products_query)
            self.FLX_LOG(DEBUG, f"products 테이블 데이터 전체 조회 결과: {type(products)}\n {products}")

            # products 테이블 데이터 1개 조회 - products 테이블 데이터 전체 조회의 쿼리 이용
            single_product = self.FLX_MySql_Select(db_session, all_products_query, is_get_one=True)
            self.FLX_LOG(DEBUG, f"products 테이블 데이터 1개 조회 결과: {type(single_product)}\n {single_product}")

            # products 테이블 조건 요청한 category인 데이터 조회
            products_by_category_query = self.FLX_Query_Load(query_num=1, replace_items={"{schema_name}": schema_name})
            category_products = self.FLX_MySql_Select(db_session, products_by_category_query, {"category": category})
            self.FLX_LOG(DEBUG, f"products 테이블 조건 요청한 category인 데이터 조회 결과: {type(category_products)}\n {category_products}")

            # products 테이블 조건 요청한 category인 데이터 갯수 조회
            products_by_category_count_query = self.FLX_Query_Load(query_num=2, replace_items={"{schema_name}": schema_name})
            category_count = self.FLX_MySql_Select(db_session, products_by_category_count_query, {"category": category}, is_scalar=True)
            self.FLX_LOG(DEBUG, f"products 테이블 조건 요청한 category인 데이터 갯수 조회 결과: {type(category_count)}\n {category_count}")
        finally:
            try:
                self.FLX_MySql_Rollback(db_session)
            finally:
                self.FLX_MySql_Release_Session(db_session)

        # msg/ExampleSelect_msg.json의 c_code, ret_code 키 값을 매핑된 메시지가 전달, 매핑될 데이터가 없는 경우 ret_msg 가 전달
        # test/ExampleSelect.json의 c_code=KOR 인 경우 "상품을 조회했습니다."
        # test/ExampleSelect.json의 c_code=USA 인 경우 "Products retrieved."
        # test/ExampleSelect.json의 c_code=CHN 인 경우 매핑된 데이터가 없어서 self.FLX_Return_Normal(ret_msg="조회가 완료되었습니다.")
        self.FLX_Return_Normal(_return=category_products, ret_code=0, ret_msg="조회가 완료되었습니다.")
