import {z} from 'zod';

export const localUrl = z.url({error: 'Gateway 주소의 URL 형식을 확인하세요.'}).refine((value) => {
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)
      && !url.username && !url.password && !url.search && !url.hash && ['/', '/api', '/v10/api'].includes(url.pathname);
  } catch {
    return false;
  }
}, {message: 'Gateway는 localhost의 /, /api 또는 /v10/api 주소를 사용하세요.'});
const identifier = z.string().regex(/^[A-Za-z0-9_][A-Za-z0-9_-]{0,63}$/);

export const gatewayConfigSchema = z.object({
  gateway: localUrl.default('http://localhost:8100/v10/api'),
  com_code: identifier.default('fluxondemo'),
  group: identifier.default('experience'),
  service: identifier.default('products'),
  c_code: identifier.default('KOR'),
  wait_sec: z.coerce.number().int().min(0).max(60).default(10),
  cache_sec: z.coerce.number().int().min(0).max(60).default(10),
  // 선택 설정이므로 생략할 수 있습니다. undefined의 처리는 Gateway 전송 함수가 담당합니다.
  waitMode: z.enum(['poll', 'cancel']).optional(),
  payloadEncryptionEnabled: z.boolean().default(false),
});

export type GatewayConfig = z.infer<typeof gatewayConfigSchema>;
// 최초 준비 점검의 정상 결과는 null 또는 'reset' 두 가지입니다.
export const productSetupSchema = z.literal('reset').nullable();
export const productCategoriesSchema = z.object({
  categories: z.array(z.string().regex(/^[A-Z_]{1,40}$/)),
});
export const productInputSchema = z.object({
  category: z.string({error: '상품 종류는 문자열이어야 합니다.'}).regex(/^[A-Z_]{1,40}$/, '상품 종류는 영문 대문자와 밑줄로 1–40자 입력하세요.').nullable(),
  limit: z.number({error: '최대 조회 수를 입력하세요.'}).int('최대 조회 수는 정수여야 합니다.').min(1, '최대 조회 수는 1 이상이어야 합니다.').max(50, '최대 조회 수는 50 이하여야 합니다.'),
  sort: z.enum(['id', 'price_asc'], {error: '정렬은 ID 순서 또는 가격 오름차순을 선택하세요.'}).optional(),
});
export type ProductInput = z.infer<typeof productInputSchema>;
export const productSchema = z.object({id: z.number().int(), name: z.string(), category: z.string(), price: z.number().int()});
export const productsSchema = z.object({items: z.array(productSchema), total: z.number().int().nonnegative()});
export type Products = z.infer<typeof productsSchema>;
export type Product = z.infer<typeof productSchema>;

// 등록·수정은 요청의 TypeScript 타입만 정의합니다. 입력 검증과 상품명 trim은 백엔드가 담당합니다.
// 빈 가격도 서버의 필수값 검사까지 전달할 수 있도록 null을 허용합니다.
export type ProductValues = {name: string; category: string; price: number | null};
export type ProductUpdate = ProductValues & {id: number};
export const productIdSchema = z.number({error: '상품 ID는 숫자여야 합니다.'}).int('상품 ID는 정수여야 합니다.').positive('상품 ID는 1 이상이어야 합니다.').max(2147483647, '상품 ID가 허용된 범위를 넘었습니다.');
export const productChangedSchema = z.object({id: productIdSchema});

