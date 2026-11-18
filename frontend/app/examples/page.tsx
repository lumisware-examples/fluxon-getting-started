import {connection} from 'next/server';
import type {Metadata} from 'next';
import {getExamplesConfig} from '@/src/features/examples/config';
import {ExamplesRunner} from './examples-runner';

export const metadata: Metadata = {title: '워크 모듈 예제 · Fluxon Getting Started'};

export default async function ExamplesPage() {
  // 서버는 공개 연결 설정만 읽습니다. DB 준비를 포함한 모든 호출은 버튼으로 실행합니다.
  await connection();
  return <ExamplesRunner defaults={getExamplesConfig()} />;
}
