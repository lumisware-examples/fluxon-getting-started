import {getGatewayConfig} from '../products/config';
import type {GatewayConfig} from '../products/model';

// 기존 공개 연결 설정을 읽되 이 페이지의 대상은 제공한 examples 서비스로 고정합니다.
// 상품 화면의 API_GROUP/API_SERVICE를 바꾸지 않고 두 서비스를 오갈 수 있습니다.
export function getExamplesConfig(): GatewayConfig {
  return {...getGatewayConfig(), group: 'demo_group', service: 'examples', cache_sec: 0};
}
