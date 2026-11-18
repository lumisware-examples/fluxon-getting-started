"""06. 공통 함수와 공통 객체를 읽어 계산합니다."""
from work_lib import *

class ExampleCommon(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        pass

    def FLX_Main_Work_Start(self):
        unit_price = self.FLX_Get_Request_Data("unit_price")
        quantity = self.FLX_Get_Request_Data("quantity")

        if type(unit_price) is not int or not 0 <= unit_price <= 2147483647:
            self.FLX_Return_Normal(ret_code=10, ret_msg="단가는 0–2147483647의 정수로 입력하세요.")
        if type(quantity) is not int or not 1 <= quantity <= 100:
            self.FLX_Return_Normal(ret_code=11, ret_msg="수량은 1–100의 정수로 입력하세요.")

        currency = self.FLX_Get_Common_Obj("examples_common", "CURRENCY")

        # FLX_Call_Common_Func() 에서 module_name은  examples_service_common.py에서 .py를 뺀 이름입니다.
        # FLX_Call_Common_Func() 에서 func_name은 examples_service_common.py에서 함수 calculate_total 입니다.
        total_case_1 = self.FLX_Call_Common_Func("examples_common", "calculate_total", unit_price, quantity)
        self.FLX_LOG(DEBUG, f"total_case_1 = {total_case_1}")

        # FLX_Get_Common_Obj() 에서 module_name은  examples_service_common.py에서 .py를 뺀 이름입니다.
        # FLX_Get_Common_Obj() 에서 attr_name은 examples_service_common.py에서 함수 calculate_total 입니다.
        obj_func = self.FLX_Get_Common_Obj("examples_common", "calculate_total")
        total_case_2 = obj_func(unit_price, quantity)
        self.FLX_LOG(DEBUG, f"total_case_2 = {total_case_2}")

        # FLX_Call_Common_Func() 에서 module_name은  examples_group_common.py에서 .py를 뺀 이름입니다.
        # FLX_Call_Common_Func() 에서 func_name은 examples_group_common.py에서 함수 calculate_total 입니다.
        total_case_3 = self.FLX_Call_Common_Func("examples_group_common", "calculate_total", unit_price, quantity)
        self.FLX_LOG(DEBUG, f"total_case_3 = {total_case_3}")

        # FLX_Get_Common_Obj() 에서 module_name은  examples_group_common.py에서 .py를 뺀 이름입니다.
        # FLX_Get_Common_Obj() 에서 attr_name은 examples_group_common.py에서 함수 calculate_total 입니다.
        obj_func = self.FLX_Get_Common_Obj("examples_group_common", "calculate_total")
        total_case_4 = obj_func(unit_price, quantity)
        self.FLX_LOG(DEBUG, f"total_case_4 = {total_case_4}")

        response = {"currency": currency, "total_case_1": total_case_1, "total_case_2": total_case_2, "total_case_3": total_case_3, "total_case_4": total_case_4}

        self.FLX_Return_Normal(response, ret_code=0, ret_msg="공통 함수로 합계를 계산했습니다.")
