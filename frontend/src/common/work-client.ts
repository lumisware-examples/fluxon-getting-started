import {localUrl, type GatewayConfig} from '../features/products/model';
import {gatewayRequest} from '../features/products/transport';

// Echo와 상품 예제가 같은 전송 경로를 사용합니다. 이 모듈을 불러오는 것만으로 요청하지 않습니다.
export function apiUrl(base: string): string {
  const url = new URL(localUrl.parse(base));
  url.pathname = '/v10/api';
  return url.href;
}

// 조회와 변경 모두 같은 Gateway 전송·암호화·오류 처리 코드를 사용합니다.
export async function callWork(config: GatewayConfig, call: string, input: Record<string, unknown>): Promise<unknown> {
  // call은 실행할 워크 모듈명, request_data는 그 모듈에 전달할 입력값입니다.
  // gatewayRequest는 접수 응답이 아니라 최종 결과를 받은 뒤에 완료됩니다.
  // 대기 방식은 config.ts에서 정합니다. undefined를 전달하면 poll로 동작합니다.
  return gatewayRequest(apiUrl(config.gateway), createWorkRequest(config, call, input), config.payloadEncryptionEnabled, config.waitMode);
}

// 실제 전송과 화면 표시가 일치하도록 암호화 전 Gateway JSON을 한 곳에서 만듭니다.
export function createWorkRequest(config: GatewayConfig, call: string, input: Record<string, unknown>) {
  return {
    case: 'work',
    c_code: config.c_code,
    com_code: config.com_code,
    group: config.group,
    service: config.service,
    call,
    request_data: input,
    cache_sec: config.cache_sec,
    wait_sec: config.wait_sec,
  };
}
