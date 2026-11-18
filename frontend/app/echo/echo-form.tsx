'use client';

import {useRef, useState, type FormEvent} from 'react';
import {useMutation} from '@tanstack/react-query';
import {Button, Code, Container, Group, Paper, SimpleGrid, Stack, Text, Textarea, Title} from '@mantine/core';
import type {GatewayConfig} from '@/src/features/products/model';
import {sendEcho} from '@/src/features/echo/client';
import {createWorkRequest} from '@/src/common/work-client';

export function EchoForm({defaults}: {defaults: GatewayConfig}) {
  const [message, setMessage] = useState('안녕하세요, Fluxon!');
  // React 상태가 화면에 반영되기 전의 빠른 연속 클릭도 한 요청으로 제한합니다.
  const sending = useRef(false);
  const echo = useMutation({
    // mutate(message)의 입력으로 Gateway를 호출하고 최종 응답까지 기다립니다.
    mutationFn: (value: string) => sendEcho(defaults, value),
    // 성공/업무 오류 알림은 공통 Provider가 ret_code와 ret_msg로 표시합니다.
    onSettled: () => {sending.current = false;},
  });

  // variables는 마지막 mutate에 전달한 값입니다. 입력창을 고쳐도 송신 기록은 바뀌지 않습니다.
  const request = echo.variables === undefined ? null
    : createWorkRequest({...defaults, cache_sec: 0}, 'ExampleEcho', {message: echo.variables});

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (sending.current || echo.isPending) return;
    sending.current = true;
    // 필수값·길이 검사를 중복 구현하지 않고 백엔드가 반환한 메시지를 사용합니다.
    echo.mutate(message);
  }

  return <Container component="main" size="lg" py={{base: 32, sm: 48}}><Stack gap="xl">
    <Stack gap="xs"><Text size="xs" fw={800} c="indigo" lts="0.1em">FLUXON GETTING STARTED</Text>
      <Title order={1}>송수신 테스트</Title>
      <Text>DB 없이 메시지를 보내고, 내 Gateway에서 돌아온 응답을 확인합니다.</Text>
    </Stack>
    <Paper withBorder p={{base: 'md', sm: 'xl'}}><form onSubmit={submit} noValidate aria-label="Echo 메시지 전송"><Stack>
      <Textarea label="보낼 메시지" description="최대 1000자. 공백과 줄바꿈을 포함해 입력한 내용을 그대로 돌려줍니다."
        value={message} onChange={(event) => setMessage(event.currentTarget.value)} minRows={4} autosize
        disabled={echo.isPending} />
      <Group><Button type="submit" loading={echo.isPending} disabled={echo.isPending} aria-busy={echo.isPending}>메시지 전송</Button></Group>
      <Text size="sm" c="dimmed" role="status">{echo.isPending ? 'Gateway 응답을 기다리고 있습니다.' : '메시지를 입력한 뒤 전송해 주세요.'}</Text>
    </Stack></form></Paper>
    {request !== null && <Stack gap="sm">
      <Text size="sm" c="dimmed">송신은 암호화 전, 수신은 복호화 후 JSON을 표시합니다.</Text>
      {/* 모바일은 한 열, sm(48em) 이상에서는 두 열로 나란히 배치합니다. */}
      <SimpleGrid cols={{base: 1, sm: 2}} spacing="lg">
        <Paper withBorder p={{base: 'md', sm: 'xl'}} miw={0} data-testid="echo-request"><Stack>
          <Title order={2} size="h3">송신 JSON</Title>
          <Code block mah={400} style={{overflow: 'auto', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere'}}>{JSON.stringify(request, null, 2)}</Code>
        </Stack></Paper>
        {echo.data !== undefined && <Paper withBorder p={{base: 'md', sm: 'xl'}} miw={0} data-testid="echo-response"><Stack>
          <Title order={2} size="h3">수신 JSON</Title>
          {/* 업무 오류도 정상 수신한 JSON이므로 ret_code/ret_msg를 확인할 수 있게 표시합니다. */}
          <Code block mah={400} style={{overflow: 'auto', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere'}}>{JSON.stringify(echo.data.raw, null, 2)}</Code>
          {echo.data.code === 0 && echo.data.data !== null && <Stack data-testid="echo-result">
            <Title order={3} size="h4">받은 메시지</Title>
            <Text style={{whiteSpace: 'pre-wrap', overflowWrap: 'anywhere'}}>{echo.data.data}</Text>
          </Stack>}
        </Stack></Paper>}
      </SimpleGrid>
    </Stack>}
  </Stack></Container>;
}
