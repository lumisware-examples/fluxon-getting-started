import { ProductQuery } from './product-query';
import { connection } from 'next/server';
import { getGatewayConfig } from '@/src/features/products/config';

export default async function Page() {
  // 요청 시점에 서버에서 공개 연결 설정을 읽어 Client Component의 props로 전달합니다.
  // 상품 API 호출은 브라우저에서 실행하며, 이 서버 컴포넌트가 중계하지 않습니다.
  await connection();
  return <ProductQuery defaults={getGatewayConfig()} />;
}
