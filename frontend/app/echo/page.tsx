import {connection} from 'next/server';
import type {Metadata} from 'next';
import {getGatewayConfig} from '@/src/features/products/config';
import {EchoForm} from './echo-form';

export const metadata: Metadata = {title: '송수신 테스트 · Fluxon Getting Started'};

export default async function EchoPage() {
  // 서버는 공개 연결 설정만 전달합니다. 실제 Gateway 요청은 브라우저에서 실행됩니다.
  await connection();
  return <EchoForm defaults={getGatewayConfig()} />;
}
