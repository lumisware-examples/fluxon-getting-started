import { productInputSchema, productsSchema, productCategoriesSchema,
  productIdSchema, productChangedSchema, productSetupSchema, type GatewayConfig, type ProductInput, type ProductValues, type ProductUpdate } from './model';
import {callWork} from '../../common/work-client';
export {apiUrl} from '../../common/work-client';
import { serviceResult } from '../../common/gateway-response';

// 준비되어 있는 call 예제
type ProductCall = 'ProductInitialDB' | 'ProductInquiry' | 'ProductSelectCategories' | 'ProductInsert' | 'ProductUpdate' | 'ProductDelete' | 'ProductReset';

export async function callProduct(config: GatewayConfig, input: ProductInput): Promise<unknown> {
  return callWork(config, 'ProductInquiry', productInputSchema.parse(input));
}

// queryFn은 이 Promise의 완료/실패를 보고 data 또는 error를 갱신합니다.
export async function queryProducts(config: GatewayConfig, input: ProductInput) {
  const raw = await callProduct(config, input);
  return serviceResult(raw, productsSchema);
}

// ProductInitialDB은 확인만 합니다. result=null이면 준비됨, "reset"이면 초기화가 필요합니다.
export async function checkProductSetup(config: GatewayConfig) {
  // 직전 성공 응답이 재사용되지 않도록 이 점검만 Gateway 캐시를 끕니다.
  const raw = await callWork({...config, cache_sec: 0}, 'ProductInitialDB', {});
  return serviceResult(raw, productSetupSchema);
}

// 한 번의 준비 요청은 점검 → 필요한 경우 초기화 1회 → 재점검 순서로 끝납니다.
// 초기화가 실패하거나 재점검에서도 reset이면 자동 반복하지 않습니다.
export async function prepareProducts(config: GatewayConfig) {
  const checked = await checkProductSetup(config);
  if (checked.code !== 0 || checked.data !== 'reset') return checked;

  const reset = await resetProducts({...config, cache_sec: 0});
  if (reset.code !== 0) return {...reset, data: null};
  return checkProductSetup(config);
}

// 준비 상태 점검에 통과한 뒤 useQuery가 상품 종류를 불러옵니다.
export async function queryProductCategories(config: GatewayConfig) {
  const raw = await callWork(config, 'ProductSelectCategories', {});
  return serviceResult(raw, productCategoriesSchema.transform((result) => Array.from(new Set(result.categories))));
}

// 업무 실패도 code/message를 반환합니다. code가 0인 경우에만 화면에서 후속 갱신을 실행합니다.
async function changeProduct(config: GatewayConfig, call: Exclude<ProductCall, 'ProductInitialDB' | 'ProductInquiry' | 'ProductSelectCategories'>, input: Record<string, unknown>) {
  const raw = await callWork(config, call, input);
  return serviceResult(raw, call === 'ProductReset' ? undefined : productChangedSchema);
}

export async function insertProduct(config: GatewayConfig, input: ProductValues) {
  // 등록 입력은 변환·검증 없이 전달하고, 백엔드의 ret_code/ret_msg로 결과를 판단합니다.
  return changeProduct(config, 'ProductInsert', input);
}

export async function updateProduct(config: GatewayConfig, input: ProductUpdate) {
  return changeProduct(config, 'ProductUpdate', input);
}

export async function deleteProduct(config: GatewayConfig, id: number) {
  return changeProduct(config, 'ProductDelete', {id: productIdSchema.parse(id)});
}

export async function resetProducts(config: GatewayConfig) {
  return changeProduct(config, 'ProductReset', {});
}
