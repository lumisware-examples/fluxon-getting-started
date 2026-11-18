"""12. 늦게 완료되는 작업으로 Gateway 결과 폴링을 확인합니다."""
from work_lib import *

import time


class ExampleDelayedResult(FLXWork):
    def __init__(self, **args):
        super().__init__(**args)

    def FLX_Main_Field_Check(self):
        self.FLX_Check_Request_Data("delay_sec", int)

    def FLX_Main_Work_Start(self):
        # wait_sec 보다 워크 모듈 수행시간이 더 긴 경우는 gateway에서 결과에 {"cid": "유일한 응답키", "status": "accepted"} 포함해서 전달합니다.
        # 이런 경우 cid로 폴링하여 결과를 비동기로 받아 처리할 수 있습니다.
        delay_sec = self.FLX_Get_Request_Data("delay_sec")
        if type(delay_sec) is not int or not 1 <= delay_sec <= 15:
            self.FLX_Return_Error(ret_code=10, ret_msg="지연 시간은 1–15초 정수로 입력하세요.")

        request_key = self.FLX_Get_UUID()
        self.FLX_LOG(INFO, f"지연 실습 시작: request_key={request_key}, delay_sec={delay_sec}")
        # DB 세션을 점유하지 않는 짧은 지연입니다. 실제 업무에서는 필요한 처리로 대체합니다.
        time.sleep(delay_sec)
        # cid·accepted·pending은 Gateway가 관리합니다. 워크 모듈에서 가짜 값을 만들지 않습니다.
        self.FLX_LOG(INFO, f"지연 실습 완료: request_key={request_key}")

        response = {"request_key": request_key, "delay_sec": delay_sec}
        self.FLX_Return_Normal(_return=response, ret_msg="지연 작업을 완료했습니다.")
