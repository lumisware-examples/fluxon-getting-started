"""02. 필수 키 검사와 업무 값 검사를 구분합니다."""
from work_lib import *


class ExampleValidation(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # 키 누락은 런타임의 최상위 error_code로 응답합니다. 타입은 바꾸지 않습니다.
        self.FLX_Check_Request_Data("name")
        self.FLX_Check_Request_Data("quantity")

    def FLX_Main_Work_Start(self):
        name = self.FLX_Get_Request_Data("name")
        quantity = self.FLX_Get_Request_Data("quantity")
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 40:
            self.FLX_Return_Normal(ret_code=10, ret_msg="이름은 공백을 제외하고 1–40자로 입력하세요.")
        # bool은 Python int의 하위 타입이므로 type(...) is int로 제외합니다.
        if type(quantity) is not int or not 1 <= quantity <= 100:
            self.FLX_Return_Normal(ret_code=11, ret_msg="수량은 1–100의 정수로 입력하세요.")

        self.FLX_Return_Normal(_return={"name": name.strip(), "quantity": quantity},
                                      ret_msg="입력값 검사를 통과했습니다.")
