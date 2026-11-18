'use client';

import {createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode} from 'react';
import {Notification, Portal, Stack} from '@mantine/core';

type SnackbarKind = 'success' | 'error';
type SnackbarMessage = {id: number; message: string; kind: SnackbarKind};
const SnackbarContext = createContext<((message: string, kind: SnackbarKind) => void) | null>(null);

function SnackbarItem({item, close}: {item: SnackbarMessage; close: (id: number) => void}) {
  useEffect(() => {
    const timer = setTimeout(() => close(item.id), 6000);
    return () => clearTimeout(timer);
  }, [item.id, close]);

  const success = item.kind === 'success';
  return <Notification color={success ? 'green' : 'red'} withBorder
    style={{boxShadow: 'var(--mantine-shadow-md)', borderColor: `var(--mantine-color-${success ? 'green' : 'red'}-6)`}}
    icon={<span aria-hidden>{success ? '✓' : '×'}</span>} onClose={() => close(item.id)}
    closeButtonProps={{'aria-label': '알림 닫기'}} role={success ? 'status' : 'alert'}
    aria-live={success ? 'polite' : 'assertive'} data-testid="snackbar" data-kind={item.kind}
    styles={{description: {whiteSpace: 'pre-wrap', overflowWrap: 'anywhere'}}}>
    {item.message}
  </Notification>;
}

// Mantine의 기본 Notification을 사용하므로 별도 알림 라이브러리는 필요하지 않습니다.
export function SnackbarProvider({children}: {children: ReactNode}) {
  const [messages, setMessages] = useState<SnackbarMessage[]>([]);
  const nextId = useRef(0);
  const show = useCallback((message: string, kind: SnackbarKind) => {
    if (!message.trim()) return; // 백엔드 메시지가 비어 있으면 임의의 성공 문구를 만들지 않습니다.
    const item = {id: ++nextId.current, message, kind};
    setMessages((current) => [...current, item].slice(-3));
  }, []);
  const close = useCallback((id: number) => setMessages((current) => current.filter((item) => item.id !== id)), []);

  return <SnackbarContext.Provider value={show}>
    {children}
    <Portal><Stack gap="sm" pos="fixed" bottom={{base: 64, sm: 16}} right={16} style={{zIndex: 1000,
      width: 'min(360px, calc(100vw - 32px))', maxHeight: 'calc(100vh - 32px)', overflowY: 'auto'}}>
      {messages.map((item) => <SnackbarItem key={item.id} item={item} close={close} />)}
    </Stack></Portal>
  </SnackbarContext.Provider>;
}

export function useSnackbar() {
  const show = useContext(SnackbarContext);
  if (!show) throw new Error('SnackbarProvider가 필요합니다.');
  return show;
}
