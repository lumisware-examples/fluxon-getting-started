"""04. 정상·업무 실패 응답과 국가별 메시지 치환을 배웁니다."""
from work_lib import *


class ExampleResponse(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        data = self.FLX_Get_Request_Data()
        outcome = data.get("outcome", "success")
        name = data.get("name", "입문자")
        if not isinstance(name, str) or not name.strip() or len(name) > 40:
            self.FLX_Return_Normal(ret_code=11, ret_msg="이름은 1–40자로 입력하세요.")
        if outcome not in ("success", "failure"):
            self.FLX_Return_Normal(ret_code=12, ret_msg="outcome은 success 또는 failure로 입력하세요.")

        if outcome == "failure":
            # Return_Error도 업무 response_data.ret_code/ret_msg를 반환하고 즉시 끝냅니다.
            # Gateway의 최상위 error_code 오류를 임의로 만드는 API가 아닙니다.
            self.FLX_Return_Error(10, "업무 실패 응답을 확인했습니다.")

        # _msg.json의 {name}을 치환합니다. KOR/USA를 바꿔 같은 코드의 문구를 비교하세요.
        self.FLX_Return_Normal(_return={"greeting": name}, ret_code=0, ret_msg="정상 응답을 확인했습니다.", name=name)
