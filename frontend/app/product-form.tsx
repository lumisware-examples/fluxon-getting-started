'use client';

import {useState, type FormEvent} from 'react';
import {Button, Fieldset, Group, NumberInput, SimpleGrid, Stack, TextInput} from '@mantine/core';
import type {Product, ProductValues} from '@/src/features/products/model';

type Props = {
  product?: Product;
  busy: boolean;
  saving: boolean;
  onSave: (input: ProductValues) => void;
  onCancel?: () => void;
};

// 등록과 수정은 같은 입력 항목을 사용합니다. ID는 수정 대상에서만 가져옵니다.
export function ProductForm({product, busy, saving, onSave, onCancel}: Props) {
  const [name, setName] = useState(product?.name ?? '');
  const [category, setCategory] = useState(product?.category ?? 'HOME');
  const [price, setPrice] = useState<number | string>(product?.price ?? '');

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    // 이름·분류·가격의 필수값/형식/범위는 백엔드가 검사합니다. 여기서 제출을 막지 않습니다.
    // NumberInput의 문자열 상태를 JSON 숫자로 바꾸고, 빈 가격은 null로 전달합니다.
    // 결과의 ret_code/ret_msg는 Provider의 공통 스낵바가 표시합니다.
    onSave({name, category, price: price === '' ? null : Number(price)});
  }

  return <form onSubmit={submit} noValidate aria-label={product ? '상품 수정 입력' : '상품 등록 입력'}><Stack>
    <Fieldset disabled={busy} variant="unstyled"><Stack>
      <TextInput label="상품명" value={name} onChange={(event) => setName(event.currentTarget.value)} withAsterisk aria-required="true" />
      <SimpleGrid cols={{base: 1, sm: 2}}>
        <TextInput label="상품 분류" description="영문 대문자·밑줄 1–40자" inputWrapperOrder={['label', 'input', 'description', 'error']} value={category} onChange={(event) => setCategory(event.currentTarget.value)} withAsterisk aria-required="true" />
        <NumberInput label="가격 (KRW)" value={price} onChange={setPrice} clampBehavior="none" withAsterisk aria-required="true" />
      </SimpleGrid>
      <Group justify="flex-end">
        {onCancel && <Button type="button" variant="default" onClick={onCancel}>취소</Button>}
        <Button type="submit" loading={saving} disabled={busy} aria-busy={saving}>{product ? '수정 저장' : '상품 등록'}</Button>
      </Group>
    </Stack></Fieldset>
  </Stack></form>;
}
