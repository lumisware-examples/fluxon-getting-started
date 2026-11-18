'use client';

import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {Button, Container, Group} from '@mantine/core';

export function ExampleNavigation() {
  const pathname = usePathname();
  // 실제 페이지 링크를 사용해 새로고침·직접 접속·뒤로 가기도 같은 경로로 동작합니다.
  return <div style={{borderBottom: '1px solid var(--mantine-color-default-border)'}}>
    <Container component="nav" aria-label="예제 메뉴" size="lg" py="md"><Group gap="sm">
      {[{href: '/', label: '상품 관리'}, {href: '/examples', label: '워크 모듈 예제'}].map((item) =>
        <Button key={item.href} component={Link} href={item.href} aria-current={pathname === item.href ? 'page' : undefined}
          variant={pathname === item.href ? 'filled' : 'default'}>{item.label}</Button>)}
    </Group></Container>
  </div>;
}
