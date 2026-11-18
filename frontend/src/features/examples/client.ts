import {callWork} from '../../common/work-client';
import {serviceResult} from '../../common/gateway-response';
import type {GatewayConfig} from '../products/model';
import type {ExampleCall} from './catalog';

export async function runExample(config: GatewayConfig, call: ExampleCall, input: Record<string, unknown>) {
  // 입력 항목의 필수값·타입·범위는 각 워크 모듈이 검사합니다.
  // 공통 전송 함수가 암복호화와 accepted/pending의 결과 폴링을 끝내면 반환합니다.
  const raw = await callWork(config, call, input);
  // 예제마다 result 구조가 다르므로 공통 ret_code/ret_msg만 판정하고 JSON 원문을 보여줍니다.
  return serviceResult(raw);
}
