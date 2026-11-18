"""
최초: 2026.10.26
내용: 처음으로 작성한 Fluxon 업무 모듈 예제
"""
from work_lib import *  # type: ignore

class FirstExample(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

        self.local_var = "local variable"

    def FLX_Main_Field_Check(self):
        self.FLX_Check_Request_Data("req_field_1", str)
        self.FLX_Check_Request_Data("req_field_2", str)

    def FLX_Main_Work_Start(self):
        req_field_1 = self.FLX_Get_Request_Data("req_field_1")
        req_field_2 = self.FLX_Get_Request_Data("req_field_2")
        self.FLX_LOG(DEBUG, f"req_field_1 = {req_field_1} req_field_2 = {req_field_2}")

        # 업무 로직 수행
        response = {
            "result_field_1": f"Processed {req_field_1}",
            "result_field_2": f"Processed {req_field_2}",
            "local_var": self.local_var
        }

        self.FLX_Return_Normal(
            _return=response,
            ret_code=100,
            ret_msg="정상 처리 완료",
        )
