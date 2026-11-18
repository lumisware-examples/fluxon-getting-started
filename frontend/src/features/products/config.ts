import { gatewayConfigSchema, type GatewayConfig } from './model';

// Server Component에서만 호출하며, 브라우저에 필요한 공개 연결 설정만 선택합니다.
export function getGatewayConfig(): GatewayConfig {
  const value = (name: string) => process.env[name]?.trim() || undefined;
  const parsed = gatewayConfigSchema.safeParse({
    gateway: value('API_SERVER'),
    com_code: value('API_COM_CODE'),
    group: value('API_GROUP'),
    service: value('API_SERVICE'),
    c_code: value('API_COUNTRY_CODE'),
    wait_sec: value('API_REQUEST_TIMEOUT_SEC'),
    cache_sec: value('API_CACHE_SEC'),
    // Gateway 요청의 기본 대기 방식입니다. undefined인 경우에도 poll로 처리합니다.
    // poll: 최종 결과까지 폴링. cancel: wait_sec 이후 응답 대기 중단.
    waitMode: 'poll',
    payloadEncryptionEnabled: process.env.BACKEND_PAYLOAD_ENCRYPTION_ENABLED === 'true',
  });
  if (!parsed.success) throw new Error('Gateway 환경변수 형식을 확인하세요. URL·회사 코드·그룹·서비스·국가 코드 및 Gateway 응답 대기·캐시 시간(0–60초)이 필요합니다.');
  return parsed.data;
}
