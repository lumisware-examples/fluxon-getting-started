import '@mantine/core/styles.css';
import './globals.css';
import { ColorSchemeScript, mantineHtmlProps } from '@mantine/core';
import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { AppProviders } from './providers';
import {ExampleNavigation} from './example-navigation';

export const metadata: Metadata = { title: 'Fluxon Getting Started', description: '내 Gateway에서 워크 모듈 예제와 상품 관리를 실행하는 입문 예제입니다.' };

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="ko" {...mantineHtmlProps}>
    <head><ColorSchemeScript defaultColorScheme="light" /></head>
    <body><AppProviders><ExampleNavigation />{children}</AppProviders></body>
  </html>;
}
