'use client';

import { createTheme, MantineProvider } from '@mantine/core';
import { useState, type ReactNode } from 'react';
import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {getErrorMessage} from '@/src/common/error-message';
import {SnackbarProvider, useSnackbar} from './snackbar';

const theme = createTheme({ primaryColor: 'indigo', defaultRadius: 'md', fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' });

function QueryProvider({children}: {children: ReactNode}) {
  const showSnackbar = useSnackbar();
  // QueryClient는 조회 결과와 요청 상태를 보관합니다. 렌더링마다 새로 만들지 않습니다.
  const [queryClient] = useState(() => {
    // HTTP 요청이 정상 완료되어도 업무 ret_code는 0이 아닐 수 있습니다.
    // 조회/변경의 공통 반환값을 보고 ret_msg 원문과 색상을 여기서 한 번만 정합니다.
    function onSuccess(data: unknown) {
      if (typeof data === 'object' && data !== null && 'code' in data && typeof data.code === 'number'
        && 'message' in data && typeof data.message === 'string') {
        showSnackbar(data.message, data.code === 0 ? 'success' : 'error');
      }
    }
    // error_code 오류, 통신 실패, 입력/응답 검증 실패는 React Query의 error로 전달됩니다.
    function onError(error: Error) {
      showSnackbar(getErrorMessage(error), 'error');
    }
    return new QueryClient({
      // 캐시의 콜백은 실제 요청마다 한 번 실행됩니다. 탭 이동이나 재렌더로 알림이 반복되지 않습니다.
      queryCache: new QueryCache({onSuccess, onError}),
      mutationCache: new MutationCache({onSuccess, onError}),
      defaultOptions: {
        queries: {retry: false, refetchOnWindowFocus: false, refetchOnReconnect: false},
        // 중복 등록을 피하기 위해 변경 요청을 자동 재시도/오프라인 보류하지 않습니다.
        mutations: {retry: false, networkMode: 'always'},
      },
    });
  });

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

export function AppProviders({children}: {children: ReactNode}) {
  return <MantineProvider theme={theme} defaultColorScheme="light">
    <SnackbarProvider><QueryProvider>{children}</QueryProvider></SnackbarProvider>
  </MantineProvider>;
}
