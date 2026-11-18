"""03. 요청값과 별도 dict의 타입을 변환합니다."""
from work_lib import *


class ExampleTypeConversion(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        # 변환된 값은 원래 request_data에 저장됩니다. 변환 실패는 Gateway 오류입니다.
        self.FLX_Check_Request_Data("quantity", int)
        self.FLX_Check_Request_Data("enabled", bool)
        self.FLX_Check_Request_Data("unit_price")

    def FLX_Main_Work_Start(self):
        data = self.FLX_Get_Request_Data()
        # 별도 dict를 지정하면 그 dict의 값만 바뀝니다.
        converted = {"unit_price": data["unit_price"]}
        self.FLX_Type_Convert("unit_price", int, data_set=converted)
        if type(data["quantity"]) is not int or not 1 <= data["quantity"] <= 100:
            self.FLX_Return_Normal(ret_code=10, ret_msg="변환된 수량은 1–100이어야 합니다.")
        if not 0 <= converted["unit_price"] <= 2147483647:
            self.FLX_Return_Normal(ret_code=11, ret_msg="변환된 단가는 0–2147483647이어야 합니다.")

        # 타입 변환은 엄격한 업무 검증과 다릅니다. int(1.9)는 1이 됩니다.
        self.FLX_Return_Normal(_return={"quantity": data["quantity"],
            "enabled": data["enabled"], "unit_price": converted["unit_price"]},
            ret_msg="문자열을 숫자와 불리언으로 변환했습니다.")
