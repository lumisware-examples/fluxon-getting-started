import {z} from 'zod';
import type {GatewayConfig} from '../products/model';
import {callWork} from '../../common/work-client';
import {serviceResult} from '../../common/gateway-response';

// 입력 검사는 백엔드가 담당하고, 프런트엔드는 성공 응답이 문자열인지 확인합니다.
export async function sendEcho(config: GatewayConfig, message: string) {
  const raw = await callWork({...config, cache_sec: 0}, 'ExampleEcho', {message});
  return serviceResult(raw, z.string());
}
