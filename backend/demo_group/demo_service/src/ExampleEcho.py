"""
최초: 2026.10.26
내용: DB 없이 받은 메시지를 그대로 반환하는 Gateway 입문 예제.
"""

from work_lib import *  # type: ignore


class ExampleEcho(FLXWork):  # type: ignore
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # 필수값/타입 오류도 아래에서 업무 ret_code로 안내합니다. 문자열로 강제 변환하지 않습니다.
        self.FLX_Check_Request_Data("message", is_exist=False)

    def FLX_Main_Work_Start(self):
        # request_data의 message 값 반환
        message = self.FLX_Get_Request_Data("message")
        if not isinstance(message, str) or not message.strip():
            return self.FLX_Return_Normal(ret_code=10, ret_msg="보낼 메시지를 입력하세요.")
        if len(message) > 1000:
            return self.FLX_Return_Normal(ret_code=11, ret_msg="메시지는 1000자 이하로 입력하세요.")

        # trim은 빈 값 확인에만 사용합니다. 공백·줄바꿈도 입력한 그대로 돌려줍니다.
        # DB 세션이나 공통 DB 함수를 호출하지 않으므로 상품 테이블이 없어도 실행됩니다.
        return self.FLX_Return_Normal(_return=message, ret_code=0, ret_msg="메시지를 받았습니다.")
