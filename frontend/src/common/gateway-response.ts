import {z} from 'zod';

const object = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const businessSchema = z.object({ret_code: z.number().int(), ret_msg: z.string().default(''), result: z.unknown().optional()});

// 오류도 수신한 JSON이 있으면 실습 화면에서 확인할 수 있게 원문을 보관합니다.
// Error를 상속하므로 기존 React Query 오류 처리와 스낵바는 그대로 사용합니다.
export class GatewayResponseError extends Error {
  constructor(message: string, readonly raw: unknown) { super(message); }
}

// Gateway 오류는 예외입니다. 백엔드가 준 error_msg를 그대로 사용합니다.
export function gatewayResponse(value: unknown): Record<string, unknown> {
  const root = object(value) && object(value.response) ? value.response : value;
  if (!object(root)) throw new Error('Gateway 응답 형식이 올바르지 않습니다.');
  if (Number(root.error_code ?? 0) !== 0) {
    throw new GatewayResponseError(typeof root.error_msg === 'string' && root.error_msg ? root.error_msg : 'Gateway 오류 메시지가 없습니다.', value);
  }
  return root;
}

// 업무 결과는 예외가 아닙니다. code/message로 돌려주어 스낵바 색상과 후속 동작을 결정합니다.
export function businessResponse(value: unknown) {
  const root = gatewayResponse(value);
  const parsed = businessSchema.safeParse(root.response_data);
  if (!parsed.success) throw new Error('서버 응답의 ret_code·ret_msg 형식이 올바르지 않습니다.');
  return {code: parsed.data.ret_code, message: parsed.data.ret_msg, result: parsed.data.result};
}

// 조회와 변경이 같은 형태를 반환하므로 React Query의 공통 콜백 한 곳에서 알림을 표시할 수 있습니다.
export function serviceResult<T>(raw: unknown, schema?: z.ZodType<T>) {
  const response = businessResponse(raw);
  let data: T | null = null;
  // 업무 실패에는 상품 데이터가 없어도 정상입니다. 성공한 응답에서만 result를 검증합니다.
  if (response.code === 0 && schema) {
    const parsed = schema.safeParse(response.result);
    if (!parsed.success) throw new Error('서버 응답의 데이터 형식이 올바르지 않습니다.');
    data = parsed.data;
  }
  return {raw, code: response.code, message: response.message, data};
}
