"""01. DB 없이 입력 문자열을 그대로 반환합니다."""
from work_lib import *


class ExampleEcho(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)
        self.local_var = "local variable"

    def FLX_Main_Field_Check(self):
        # request_data 로 들어온 request_data의 message 키가 없으면 error_code로 반환합니다.
        self.FLX_Check_Request_Data("message_1")
        self.FLX_Check_Request_Data("message_2", is_exist=False)

    def FLX_Main_Work_Start(self):
        message_1 = self.FLX_Get_Request_Data("message_1")
        message_2 = self.FLX_Get_Request_Data("message_2")

        if not isinstance(message_1, str) or not message_1.strip():
            self.FLX_Return_Error(ret_code=10, ret_msg="보낼 메시지를 입력하세요.")
        if len(message_1) > 1000:
            self.FLX_Return_Error(ret_code=11, ret_msg="메시지는 1000자 이하로 입력하세요.")

        response = {
            "message_1": message_1,
            "message_2": message_2,
            "local_var": self.local_var
        }

        # strip은 빈 값 검사에만 사용합니다. 실제 응답은 공백·줄바꿈을 유지합니다.
        self.FLX_Return_Normal(_return=response, ret_msg="메시지를 받았습니다.")
