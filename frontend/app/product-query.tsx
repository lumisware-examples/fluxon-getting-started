'use client';

import {useRef, useState, type FormEvent} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {Accordion, Alert, Button, Code, Container, Fieldset, Group, Loader, Modal, NumberInput, Paper, Select, SimpleGrid, Stack, Table, Tabs, Text, Title} from '@mantine/core';
import {prepareProducts, deleteProduct, insertProduct, queryProductCategories, queryProducts, resetProducts, updateProduct} from '@/src/features/products/client';
import type {GatewayConfig, Product, ProductUpdate, ProductValues} from '@/src/features/products/model';
import {ProductForm} from './product-form';
import {getErrorMessage} from '@/src/common/error-message';

export function ProductQuery({defaults}: {defaults: GatewayConfig}) {
  // Provider가 만든 QueryClient를 가져옵니다. 조회 캐시를 무효화하거나 지울 때 사용합니다.
  const queryClient = useQueryClient();
  // 입력값·선택한 탭처럼 화면 안에서만 쓰는 값은 useState로 관리합니다.
  // 서버 데이터·요청 중 여부·오류는 아래의 useQuery/useMutation이 관리합니다.
  const [activeTab, setActiveTab] = useState('query');
  const [category, setCategory] = useState('ALL');
  const [limit, setLimit] = useState<number | string>(50);
  const [sort, setSort] = useState('id');
  const [editing, setEditing] = useState<Product | null>(null);
  const [deleting, setDeleting] = useState<Product | null>(null);
  const [resetOpen, setResetOpen] = useState(false);
  const [formVersion, setFormVersion] = useState(0);
  // React Query의 상태 반영 전 연속 클릭도 중복 변경으로 전송하지 않습니다.
  const requestLock = useRef(false);

  // 1. 접속하면 점검하고, result가 reset이면 ProductReset 실행 후 다시 점검합니다.
  const initializationQuery = useQuery({
    queryKey: ['product-init', defaults],
    queryFn: () => prepareProducts(defaults),
    // 초기화가 포함될 수 있으므로 준비 작업 전체를 자동 재시도하지 않습니다.
    retry: false,
    staleTime: Infinity,
    // 화면에 다시 접속했을 때도 캐시에 남은 성공만 믿지 않고 현재 상태를 확인합니다.
    refetchOnMount: 'always',
  });
  const databaseReady = initializationQuery.isSuccess && initializationQuery.data.code === 0 && initializationQuery.data.data === null;
  const checkingDatabase = initializationQuery.isPending || initializationQuery.isFetching;
  const initializationFailed = initializationQuery.isError || (initializationQuery.isSuccess && !databaseReady);
  const initializationMessage = initializationQuery.isError
    ? getErrorMessage(initializationQuery.error) : initializationQuery.data?.message || '상품 초기화 후에도 ID 자동 발급이 준비되지 않았습니다. 다시 확인해 주세요.';

  // 2. 테이블 점검에 통과해야 상품 종류를 읽습니다. 실패한 테이블로 조회를 먼저 보내지 않습니다.
  const categoriesQuery = useQuery({
    // queryKey는 캐시의 이름입니다. Gateway 연결 설정이 다르면 별개의 결과로 구분합니다.
    queryKey: ['product-categories', defaults],
    // queryFn이 반환한 값은 data에, 던진 오류는 error에 들어갑니다.
    queryFn: () => queryProductCategories(defaults),
    enabled: databaseReady && !checkingDatabase,
    // 자동으로 오래된 결과로 취급하지 않습니다. 상품 변경 후 명시적으로 무효화해 갱신합니다.
    staleTime: Infinity,
  });
  const categoryOptions = Array.from(new Set(['ALL', ...(categoriesQuery.data?.data ?? [])]))
    .map((value) => ({value, label: value}));
  // 마지막 상품을 삭제해도 현재 선택한 조회 조건을 화면에 유지합니다.
  if (!categoryOptions.some((option) => option.value === category)) {
    categoryOptions.push({value: category, label: `${category} (현재 선택)`});
  }

  // 3. 상품 목록은 버튼으로 조회합니다. 폼 조건을 queryKey에 넣어 조건별 결과를 구분합니다.
  const productQuery = useQuery({
    queryKey: ['products', defaults, {category, limit, sort}],
    // Gateway의 최종 결과(결과 폴링 포함)가 올 때까지 이 Promise는 완료되지 않습니다.
    queryFn: () => {
      if (typeof limit !== 'number' || !Number.isInteger(limit) || limit < 1 || limit > 50) {
        throw new Error('최대 조회 수는 1–50 사이의 정수로 입력하세요.');
      }
      return queryProducts(defaults, {category: category === 'ALL' ? null : category,
        limit, ...(sort === 'price_asc' ? {sort: 'price_asc'} : {})});
    },
    // 화면 진입·입력 변경만으로 조회하지 않고, submit에서 refetch()할 때 실행합니다.
    enabled: false,
  });

  // 4. 변경 성공 후에는 DB의 최신 결과로 조회 캐시를 갱신합니다.
  async function refreshProducts() {
    // 등록·수정·삭제·초기화로 달라진 상품 종류도 다시 불러옵니다.
    await queryClient.invalidateQueries({queryKey: ['product-categories', defaults], refetchType: 'none'});
    const categoriesRefresh = categoriesQuery.refetch({cancelRefetch: false});
    // 다른 조회 조건의 캐시도 오래된 결과로 표시하지 않게 무효화합니다.
    await queryClient.invalidateQueries({queryKey: ['products', defaults], refetchType: 'none'});
    // 현재 화면에서 사용하지 않는 조건의 캐시는 지워 변경 전 목록이 다시 보이지 않게 합니다.
    queryClient.removeQueries({queryKey: ['products', defaults], predicate: (query) => query.getObserversCount() === 0});
    // enabled:false인 수동 조회는 invalidateQueries만으로 다시 실행되지 않습니다.
    // 조회 실패는 query의 오류로 표시하며, 이미 성공한 변경을 재실행하지 않습니다.
    // 서로 독립적인 두 조회는 함께 기다려 불필요한 직렬 대기 시간을 줄입니다.
    // 등록·수정·삭제 자체를 다시 실행하는 것이 아니라, 완료 후 읽기만 갱신합니다.
    await Promise.all([categoriesRefresh, productQuery.refetch({cancelRefetch: false})]);
  }

  function finishChange() {requestLock.current = false;}

  // 5. useMutation은 등록·수정·삭제 같은 변경 요청의 상태를 관리합니다.
  // mutate(input) → mutationFn(input) → 정상 응답이면 onSuccess → 성공/실패 모두 onSettled 순서입니다.
  // onSuccess는 HTTP/전송 성공을 뜻하므로, 업무 code가 0인지 확인한 뒤 화면을 갱신합니다.
  // onSuccess가 refreshProducts()를 await하므로 목록 갱신까지 isPending이 유지됩니다.
  // 알림은 Provider의 공통 콜백에서 표시하며, 성공한 변경 요청을 자동 재전송하지 않습니다.
  const insertMutation = useMutation({
    // 등록 폼에서 mutate(input)에 넣은 값이 이 함수의 input으로 전달됩니다.
    mutationFn: (input: ProductValues) => insertProduct(defaults, input),
    onSuccess: async (response) => {
      if (response.code !== 0) return;
      await refreshProducts();
      setFormVersion((version) => version + 1);
    },
    // 실패해도 입력 잠금을 풀어 사용자가 결과를 확인하고 다음 작업을 할 수 있게 합니다.
    onSettled: finishChange,
  });
  const updateMutation = useMutation({
    mutationFn: (input: ProductUpdate) => updateProduct(defaults, input),
    onSuccess: async (response) => {
      if (response.code !== 0) return;
      await refreshProducts();
      setEditing(null);
    },
    onSettled: finishChange,
  });
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteProduct(defaults, id),
    onSuccess: async (response) => {
      if (response.code !== 0) return;
      await refreshProducts();
      setDeleting(null);
    },
    onSettled: finishChange,
  });
  const resetMutation = useMutation({
    mutationFn: () => resetProducts(defaults),
    onSuccess: async (response) => {
      if (response.code !== 0) return;
      // 초기화 성공만으로 잠금을 풀지 않고 새 테이블의 AUTO_INCREMENT를 다시 확인합니다.
      const checked = await initializationQuery.refetch({cancelRefetch: false});
      setResetOpen(false);
      setFormVersion((version) => version + 1);
      if (checked.isError || checked.data?.code !== 0 || checked.data.data !== null) return;
      await refreshProducts();
    },
    onSettled: finishChange,
  });

  // isFetching은 실제 조회 중, isPending은 변경 요청과 성공 후 갱신이 진행 중인 상태입니다.
  // 아직 한 번도 조회하지 않았을 때도 query.isPending은 true일 수 있어 로더에는 isFetching을 씁니다.
  const mutations = [insertMutation, updateMutation, deleteMutation, resetMutation];
  const changing = mutations.some((mutation) => mutation.isPending);
  const busy = checkingDatabase || productQuery.isFetching || categoriesQuery.isFetching || changing;
  const productsDisabled = busy || !databaseReady;
  const categoryFailed = categoriesQuery.isError || (categoriesQuery.data !== undefined && categoriesQuery.data.code !== 0);
  const queryFailed = productQuery.isError || (productQuery.data !== undefined && productQuery.data.code !== 0);
  const products = databaseReady && productQuery.isSuccess ? productQuery.data.data : null;

  function change(action: () => void, needsReady = true) {
    // 초기화는 준비 전에도 실행할 수 있고, 나머지 변경은 점검 통과 후에만 보냅니다.
    if (busy || requestLock.current || (needsReady && !databaseReady)) return;
    requestLock.current = true;
    // reset()은 이전 성공/오류 표시만 비웁니다. DB 데이터 초기화 요청과는 다릅니다.
    mutations.forEach((mutation) => mutation.reset());
    action();
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (productsDisabled || requestLock.current) return;
    requestLock.current = true;
    // refetch()가 enabled:false인 조회를 실행합니다. 진행 중인 조회를 새 요청으로 취소하지 않습니다.
    // Gateway의 시간 제한 정책은 transport.ts의 waitMode가 담당합니다.
    void productQuery.refetch({cancelRefetch: false}).finally(() => {requestLock.current = false;});
  }

  // 조회 data/isFetching으로 결과와 로딩을 렌더링합니다. 성공/오류 메시지는 공통 스낵바가 담당합니다.
  const listContent = <Stack gap="xl">
    <Paper withBorder p={{base: 'md', sm: 'xl'}}><form onSubmit={submit}><Stack>
      <Title order={2} size="h3">{activeTab === 'update' ? '수정할 상품 조회' : activeTab === 'delete' ? '삭제할 상품 조회' : '상품 조회'}</Title>
      <Fieldset disabled={productsDisabled} variant="unstyled"><SimpleGrid cols={{base: 1, xs: 2, md: 4}} spacing="md">
        <Select label="상품 종류" data={categoryOptions} value={category} allowDeselect={false}
          rightSection={categoriesQuery.isFetching ? <Loader size="xs" aria-label="상품 종류 불러오는 중" /> : undefined}
          onChange={(value) => setCategory(value ?? 'ALL')} />
        <NumberInput label="최대 조회 수" min={1} max={50} allowDecimal={false} value={limit} onChange={setLimit} />
        <Select label="정렬" data={[{value: 'id', label: 'ID 순서'}, {value: 'price_asc', label: '가격 오름차순'}]} value={sort} onChange={(value) => setSort(value ?? 'id')} allowDeselect={false} />
        <Group align="end" h="100%"><Button type="submit" fullWidth loading={productQuery.isFetching} disabled={productsDisabled} aria-label="상품 조회" aria-busy={productQuery.isFetching}>상품 조회</Button></Group>
      </SimpleGrid></Fieldset>
      <Text size="sm" c="dimmed" role="status" aria-live="polite">{!databaseReady ? '테이블 준비 상태를 확인한 뒤 상품을 조회할 수 있습니다.' : changing ? '상품 변경과 목록 갱신을 처리하고 있습니다.' : productQuery.isFetching ? 'Gateway에서 상품을 조회하고 있습니다.' : queryFailed ? '상품 조회로 목록을 다시 확인하세요.' : products ? '상품 조회를 완료했습니다.' : '조회 조건을 선택한 뒤 상품 조회를 눌러 주세요.'}</Text>

    </Stack></form></Paper>
    {products && <Paper withBorder p={{base: 'md', sm: 'xl'}} data-testid="product-results" aria-busy={busy}><Stack>
      <Title order={2} size="h3">조회 결과</Title>
      <Text>조건에 맞는 전체 상품 {products.total}개 · 표시 {products.items.length}개</Text>
      <Table.ScrollContainer minWidth={activeTab === 'query' ? 440 : 550}><Table>
        <Table.Thead><Table.Tr><Table.Th>id</Table.Th><Table.Th>name</Table.Th><Table.Th>category</Table.Th><Table.Th>price(KRW)</Table.Th>{activeTab !== 'query' && <Table.Th>작업</Table.Th>}</Table.Tr></Table.Thead>
        <Table.Tbody>{products.items.map((product) => <Table.Tr key={product.id}>
          <Table.Td>{product.id}</Table.Td><Table.Td>{product.name}</Table.Td><Table.Td>{product.category}</Table.Td><Table.Td>{product.price.toLocaleString('ko-KR')}</Table.Td>
          {activeTab !== 'query' && <Table.Td><Group gap="xs" wrap="nowrap">
            {activeTab === 'update' && <Button size="compact-sm" variant="light" disabled={productsDisabled} aria-label={`${product.name} 수정`} onClick={() => {if (!requestLock.current) setEditing(product);}}>수정</Button>}
            {activeTab === 'delete' && <Button size="compact-sm" variant="light" color="red" disabled={productsDisabled} aria-label={`${product.name} 삭제`} onClick={() => {if (!requestLock.current) setDeleting(product);}}>삭제</Button>}
          </Group></Table.Td>}
        </Table.Tr>)}</Table.Tbody>
      </Table></Table.ScrollContainer>
      {products.items.length === 0 && <Text>조건에 맞는 상품이 없습니다.</Text>}
      <Accordion><Accordion.Item value="response"><Accordion.Control>수신 JSON</Accordion.Control><Accordion.Panel><Code block mah={400} style={{overflow: 'auto'}}>{JSON.stringify(productQuery.data?.raw, null, 2)}</Code></Accordion.Panel></Accordion.Item></Accordion>
    </Stack></Paper>}
  </Stack>;

  return <Container component="main" size="lg" py={{base: 32, sm: 64}}><Stack gap="xl">
    <Stack gap="xs"><Text size="xs" fw={800} c="indigo" lts="0.1em">FLUXON GETTING STARTED</Text>
      <Title order={1}>상품 관리</Title>
      <Text>내 Gateway에서 상품을 조회하고 등록·수정·삭제·초기화를 실행합니다.</Text>
    </Stack>
    {checkingDatabase && <Group role="status" aria-live="polite" data-testid="database-init-loading">
      <Loader size="sm" /><Text size="sm">상품 테이블을 확인하고 ID 자동 발급을 준비하고 있습니다.</Text>
    </Group>}
    {initializationFailed && !checkingDatabase && <Alert color="red" title="상품 테이블을 확인해 주세요" role="alert" data-testid="database-init-error">
      <Stack gap="sm"><Text size="sm">{initializationMessage}</Text><Group>
        <Button size="xs" variant="default" disabled={busy} onClick={() => {if (!requestLock.current) void initializationQuery.refetch({cancelRefetch: false});}}>준비 상태 다시 확인</Button>
      </Group></Stack>
    </Alert>}
    <Tabs value={activeTab} onChange={(value) => {if (!busy && !requestLock.current && value) setActiveTab(value);}} keepMounted={false} variant="outline">
      <Tabs.List grow aria-label="상품 관리 기능">
        {[{value: 'query', label: '조회'}, {value: 'insert', label: '등록'}, {value: 'update', label: '수정'}, {value: 'delete', label: '삭제'}, {value: 'reset', label: '초기화'}].map((tab) =>
          <Tabs.Tab key={tab.value} value={tab.value} disabled={busy || (!databaseReady && tab.value !== 'reset')} px="xs">{tab.label}</Tabs.Tab>)}
      </Tabs.List>
      {databaseReady && categoryFailed && <Group mt="lg">
        <Button size="xs" variant="light" disabled={busy} onClick={() => {if (!requestLock.current) void categoriesQuery.refetch();}}>상품 종류 다시 불러오기</Button>
      </Group>}
      {['query', 'update', 'delete'].map((value) => <Tabs.Panel key={value} value={value} pt="lg">{listContent}</Tabs.Panel>)}
      {/* 등록 폼은 숨겨져도 입력값이 유지되도록 마운트를 유지합니다. */}
      <Tabs.Panel value="insert" pt="lg" keepMounted>
        <Paper withBorder p={{base: 'md', sm: 'xl'}}><Stack>
          <Title order={2} size="h3">상품 등록</Title><Text size="sm" c="dimmed">상품 ID는 백엔드에서 정합니다.</Text>
          <ProductForm key={formVersion} busy={productsDisabled} saving={insertMutation.isPending} onSave={(input) => change(() => insertMutation.mutate(input))} />
        </Stack></Paper>
      </Tabs.Panel>
      <Tabs.Panel value="reset" pt="lg">
        <Paper withBorder p={{base: 'md', sm: 'xl'}}><Stack>
          <Title order={2} size="h3">예제 상품 초기화</Title>
          <Text size="sm">상품 테이블을 삭제하고 다시 만들어 기본 예제 상품 5개로 되돌립니다. 상품 ID도 처음부터 시작합니다.</Text>
          <Group><Button color="red" variant="light" disabled={busy} onClick={() => {if (!requestLock.current) setResetOpen(true);}}>상품 초기화</Button></Group>
        </Stack></Paper>
      </Tabs.Panel>
    </Tabs>

    <Modal opened={editing !== null} onClose={() => {if (!busy) setEditing(null);}} title={`상품 수정 · ID ${editing?.id ?? ''}`} closeOnClickOutside={!busy} closeOnEscape={!busy} withCloseButton={!busy}>
      {editing && <ProductForm key={editing.id} product={editing} busy={productsDisabled} saving={updateMutation.isPending} onCancel={() => setEditing(null)} onSave={(input) => change(() => updateMutation.mutate({...input, id: editing.id}))} />}
    </Modal>
    <Modal opened={deleting !== null} onClose={() => {if (!busy) setDeleting(null);}} title="상품 삭제 확인" closeOnClickOutside={!busy} closeOnEscape={!busy} withCloseButton={!busy}><Stack>
      <Text>{deleting?.name} (ID {deleting?.id}) 상품을 삭제합니다.</Text>
      <Group justify="flex-end"><Button variant="default" disabled={busy} onClick={() => setDeleting(null)}>취소</Button>
        <Button color="red" loading={deleteMutation.isPending} aria-busy={deleteMutation.isPending} disabled={busy} onClick={() => {if (deleting) change(() => deleteMutation.mutate(deleting.id));}}>삭제 실행</Button></Group>
    </Stack></Modal>
    <Modal opened={resetOpen} onClose={() => {if (!busy) setResetOpen(false);}} title="상품 초기화 확인" closeOnClickOutside={!busy} closeOnEscape={!busy} withCloseButton={!busy}><Stack>
      <Text>현재 상품 테이블과 데이터를 삭제하고, ID가 자동 발급되는 테이블에 예제 상품 5개를 다시 저장합니다. 초기화할까요?</Text>
      <Group justify="flex-end"><Button variant="default" disabled={busy} onClick={() => setResetOpen(false)}>취소</Button>
        <Button color="red" loading={resetMutation.isPending} aria-busy={resetMutation.isPending} disabled={busy} onClick={() => change(() => resetMutation.mutate(), false)}>초기화 실행</Button></Group>
    </Stack></Modal>
  </Stack></Container>;
}
