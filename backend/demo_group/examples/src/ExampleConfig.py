"""05. svc_info에서 설정을 읽고 중첩 값을 추출합니다."""
from work_lib import *


class ExampleConfig(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        # 서비스 → 그룹 → 회사 순서로 검색합니다. 파일명을 사용자 입력으로 받지 않습니다.
        # svc_info의 examples_lesson.json 파일의 내용을 dict으로 가져옵니다.
        config = self.FLX_Get_Info_Read("examples_lesson.json")
        # config (svc_info/examples_lesson.json 파일)의 {"lesson": {"title": "Fluxon 워크 모듈 입문"}} title의 값을 가져옵니다.
        title = self.FLX_Get_Info_Values(config, "lesson.title")
        # config (svc_info/examples_lesson.json 파일)의 {""pricing": {"currency": "KRW","unit_price": 1000} 에서 currency, unit_price 를 각각의 변수로 가져옵니다.
        currency, unit_price = self.FLX_Get_Info_Values(config, ["pricing.currency", "pricing.unit_price"])
        # 공개 실습 설정만 반환합니다. 설정 파일 전체나 DB 비밀값을 반환하지 않습니다.

        response = {"title": title, "currency": currency, "unit_price": unit_price}

        self.FLX_Return_Normal(_return=response, ret_msg="실습 설정을 읽었습니다.")
