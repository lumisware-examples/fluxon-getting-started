'use client';

import {useRef, useState} from 'react';
import {useMutation} from '@tanstack/react-query';
import {Alert, Badge, Button, Code, Container, Group, JsonInput, Loader, Paper, Select, SimpleGrid, Stack, Text, Title} from '@mantine/core';
import {EXAMPLES, type ExampleCall, type ExamplePreset} from '@/src/features/examples/catalog';
import {runExample} from '@/src/features/examples/client';
import type {GatewayConfig} from '@/src/features/products/model';
import {createWorkRequest} from '@/src/common/work-client';
import {GatewayResponseError} from '@/src/common/gateway-response';
import {getErrorMessage} from '@/src/common/error-message';

type RunInput = {call: ExampleCall; input: Record<string, unknown>; config: GatewayConfig};
type RunRecord = {
  request: ReturnType<typeof createWorkRequest>;
  response?: unknown;
  error?: string;
  status: 'pending' | 'success' | 'business-error' | 'error';
};

const statusLabels = {pending: '실행 중', success: '완료', 'business-error': '업무 실패', error: '요청 오류'};
const statusColors = {pending: 'blue', success: 'green', 'business-error': 'red', error: 'red'};
const jsonStyle = {overflow: 'auto', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere'} as const;

export function ExamplesRunner({defaults}: {defaults: GatewayConfig}) {
  const [selected, setSelected] = useState<ExampleCall>('ExampleEcho');
  const [country, setCountry] = useState(defaults.c_code);
  // 입력과 마지막 실행 결과를 call별로 보관해 예제를 전환해도 서로 섞이지 않게 합니다.
  const [inputs, setInputs] = useState<Partial<Record<ExampleCall, string>>>({});
  const [records, setRecords] = useState<Partial<Record<ExampleCall, RunRecord>>>({});
  const [inputError, setInputError] = useState<string | null>(null);
  const sending = useRef(false);
  const example = EXAMPLES.find((item) => item.call === selected) ?? EXAMPLES[0];
  const input = inputs[selected] ?? JSON.stringify(example.defaultInput, null, 2);
  const record = records[selected];

  // useMutation은 버튼 실행과 최종 결과의 상태를 관리합니다. 페이지 접속으로는 실행하지 않습니다.
  const execution = useMutation({
    mutationFn: ({call, input, config}: RunInput) => runExample(config, call, input),
    onSuccess: (response, variables) => {
      setRecords((current) => ({...current, [variables.call]: {
        request: createWorkRequest(variables.config, variables.call, variables.input),
        response: response.raw,
        status: response.code === 0 ? 'success' : 'business-error',
      }}));
    },
    onError: (error, variables) => {
      setRecords((current) => ({...current, [variables.call]: {
        request: createWorkRequest(variables.config, variables.call, variables.input),
        // Gateway 오류 JSON도 표시합니다. 네트워크 실패에는 가짜 수신 JSON을 만들지 않습니다.
        response: error instanceof GatewayResponseError ? error.raw : undefined,
        error: getErrorMessage(error), status: 'error',
      }}));
    },
    // 공통 Provider가 성공/실패 스낵바를 표시합니다. 중복 알림을 여기서 추가하지 않습니다.
    onSettled: () => {sending.current = false;},
  });
  const busy = execution.isPending;
  const setupRunning = busy && execution.variables?.call === 'ExampleMysqlSetup';
  const countries = Array.from(new Set(['KOR', 'USA', country])).map((value) => ({
    value, label: value === 'KOR' ? '한국어 (KOR)' : value === 'USA' ? '영어 (USA)' : value,
  }));

  function start(call: ExampleCall, value: Record<string, unknown>) {
    // React가 isPending을 반영하기 전 빠른 연속 클릭도 한 요청으로 제한합니다.
    if (sending.current || busy) return;
    sending.current = true;
    setInputError(null);
    const config = {...defaults, c_code: country,
      // 3초 지연 예제에서 Gateway의 결과 폴링을 관찰하도록 대기는 1초로 보냅니다.
      ...(call === 'ExampleDelayedResult' ? {wait_sec: 1} : {}),
    };
    // 실제 전송과 동일한 config/input을 기록합니다. 이후 입력을 고쳐도 송신 기록은 바뀌지 않습니다.
    setRecords((current) => ({...current, [call]: {
      request: createWorkRequest(config, call, value), status: 'pending',
    }}));
    execution.mutate({call, input: value, config});
  }

  function executeSelected() {
    if (sending.current || busy) return;
    let value: unknown;
    try { value = JSON.parse(input) as unknown; }
    catch { setInputError('JSON 문법을 확인하세요. 문자열은 큰따옴표로 입력합니다.'); return; }
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
      setInputError('request_data는 중괄호로 감싼 JSON 객체로 입력하세요.'); return;
    }
    // JSON 문법과 객체 여부만 검사합니다. 업무 입력 검사는 백엔드 응답으로 학습합니다.
    start(selected, value as Record<string, unknown>);
  }

  function loadPreset(preset: ExamplePreset) {
    if (sending.current || busy) return;
    setInputs((current) => ({...current, [selected]: JSON.stringify(preset.input, null, 2)}));
    if (preset.country) setCountry(preset.country);
    setInputError(null);
  }

  return <Container component="main" size="lg" py={{base: 32, sm: 48}}><Stack gap="xl">
    <Stack gap="xs">
      <Text size="xs" fw={800} c="indigo" lts="0.1em">FLUXON GETTING STARTED</Text>
      <Title order={1}>워크 모듈 예제</Title>
      <Text>예제 12개와 DB 준비 모듈을 실행하고, 송수신 JSON을 비교합니다.</Text>
      <Text size="sm" c="dimmed">요청 대상: {defaults.com_code} / {defaults.group} / {defaults.service}</Text>
    </Stack>

    <Paper withBorder p={{base: 'md', sm: 'xl'}}><Stack>
      <Title order={2} size="h3">MySQL 실습 준비</Title>
      <Text size="sm">MySQL 예제를 시작하기 전에 ExampleMysqlSetup을 실행하세요. 전용 실습 테이블이 없으면 생성하고, 이미 있으면 기존 행과 ID를 유지합니다.</Text>
      <Group><Button loading={setupRunning} disabled={busy} aria-busy={setupRunning} onClick={() => {
        if (sending.current || busy) return;
        setSelected('ExampleMysqlSetup');
        start('ExampleMysqlSetup', {});
      }}>ExampleMysqlSetup 실행</Button>
        <Text size="sm" c="dimmed">페이지 접속 시에는 테이블을 생성하지 않습니다.</Text></Group>
    </Stack></Paper>

    <Paper withBorder p={{base: 'md', sm: 'xl'}}><Stack>
      <SimpleGrid cols={{base: 1, sm: 2}}>
        <Select label="실행할 예제" value={selected} allowDeselect={false} searchable disabled={busy}
          data={EXAMPLES.map((item) => ({value: item.call, label: item.label}))}
          onChange={(value) => {
            if (sending.current || busy) return;
            const next = EXAMPLES.find((item) => item.call === value);
            if (next) {setSelected(next.call); setInputError(null);}
          }} />
        <Select label="응답 메시지 언어" value={country} data={countries} allowDeselect={false} disabled={busy}
          onChange={(value) => {if (!sending.current && value) setCountry(value);}} />
      </SimpleGrid>
      <Group gap="xs"><Title order={2} size="h3">{example.call}</Title>
        <Badge variant="light" color={example.needsDatabase ? 'orange' : 'gray'}>{example.needsDatabase ? 'MySQL 사용' : 'DB 없이 실행'}</Badge>
      </Group>
      <Text>{example.description}</Text>
      <Text size="sm" c="dimmed">{example.hint}</Text>
      <Group gap="xs">
        <Button size="xs" variant="default" disabled={busy} onClick={() => loadPreset({label: '기본 입력', input: example.defaultInput})}>기본 입력</Button>
        {example.presets.map((preset) => <Button key={preset.label} size="xs" variant="light" disabled={busy}
          onClick={() => loadPreset(preset)}>{preset.label}</Button>)}
      </Group>
      <JsonInput label="입력 JSON (request_data)" value={input} disabled={busy} formatOnBlur autosize minRows={5} maxRows={14}
        validationError="JSON 문법을 확인하세요." error={inputError}
        description="입력 예시를 고치거나 직접 작성하세요. 필수값·타입·범위 검사는 워크 모듈이 담당합니다."
        onChange={(value) => {setInputs((current) => ({...current, [selected]: value})); setInputError(null);}} />
      <Group><Button loading={busy && execution.variables?.call === selected} disabled={busy} aria-busy={busy}
        onClick={executeSelected}>선택한 예제 실행</Button>
        <Text size="sm" c="dimmed" role="status">{busy ? 'Gateway의 최종 응답을 기다리고 있습니다.' : '준비된 입력 버튼은 입력값만 바꾸며, 실행 버튼을 눌러야 요청합니다.'}</Text>
      </Group>
    </Stack></Paper>

    <Stack gap="sm">
      <Group><Title order={2} size="h3">마지막 실행 기록 · {selected}</Title>
        {record && <Badge color={statusColors[record.status]}>{statusLabels[record.status]}</Badge>}
      </Group>
      <Text size="sm" c="dimmed">송신은 암호화 전, 수신은 복호화 후 최종 JSON입니다. 예제를 전환해도 각 예제의 마지막 기록은 유지됩니다.</Text>
      {/* 좁은 화면은 위아래로, sm 이상에서는 좌우로 배치합니다. */}
      <SimpleGrid cols={{base: 1, sm: 2}} spacing="lg">
        <Paper withBorder p={{base: 'md', sm: 'xl'}} miw={0} data-testid="example-request"><Stack>
          <Title order={3} size="h4">송신 JSON</Title>
          {record ? <Code block mah={420} style={jsonStyle}>{JSON.stringify(record.request, null, 2)}</Code>
            : <Text size="sm" c="dimmed">아직 이 예제를 실행하지 않았습니다.</Text>}
        </Stack></Paper>
        <Paper withBorder p={{base: 'md', sm: 'xl'}} miw={0} data-testid="example-response" aria-busy={record?.status === 'pending'}><Stack>
          <Title order={3} size="h4">수신 JSON</Title>
          {record?.status === 'pending' ? <Group role="status"><Loader size="sm" /><Text size="sm">응답 대기 중입니다.</Text></Group>
            : record?.response !== undefined ? <Code block mah={420} style={jsonStyle}>{JSON.stringify(record.response, null, 2)}</Code>
              : <Text size="sm" c="dimmed">{record?.error ? '표시할 수신 JSON이 없습니다.' : '실행 후 Gateway 응답이 표시됩니다.'}</Text>}
          {record?.error && <Alert color="red" title="요청 오류">{record.error}</Alert>}
        </Stack></Paper>
      </SimpleGrid>
    </Stack>
  </Stack></Container>;
}
