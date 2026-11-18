import { encryptPayloadRequest, decryptPayloadResponse, importPayloadPublicKey, isPayloadEnvelope } from '../../common/payload-crypto';
import {businessResponse, gatewayResponse} from '../../common/gateway-response';

export class TransportError extends Error { constructor(readonly status: number) { super(`Gateway HTTP 오류 (${status})`); } }
export class NetworkRequestError extends Error { constructor(cause: unknown) { super('Gateway에 연결할 수 없습니다. Docker와 Gateway 실행 상태, URL 및 CORS 설정을 확인하세요.', { cause }); } }
export class GatewayTimeoutError extends Error {
  constructor(readonly waitSeconds: number) {
    super(`Gateway 응답 대기 시간(${waitSeconds}초)을 초과했습니다. 서버 처리 여부는 목록이나 Gateway 로그에서 확인하세요.`);
  }
}

// poll: 최종 결과까지 계속 기다립니다. cancel: wait_sec를 넘으면 브라우저의 응답 대기를 중단합니다.
export type GatewayWaitMode = 'poll' | 'cancel';
const defaultWaitSeconds = 10;
const defaultCacheSeconds = 10;
const validCid = (value: unknown): value is string => typeof value === 'string' && /^[A-Za-z0-9_-]{16,128}$/.test(value);
const isObject = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);
// accepted는 접수 완료, pending은 처리 중입니다. 업무 성공/실패를 뜻하는 최종 결과는 아닙니다.
const pending = (value: unknown): boolean => isObject(value) && ['accepted', 'pending'].includes(String(value.status)) && Number(value.error_code ?? 0) === 0;

// 응답을 한 번에 무제한 읽지 않고, 크기 제한 안에서 UTF-8 문자열로 읽습니다.
export async function readText(source: Request | Response, maxBytes = 2 * 1024 * 1024): Promise<string> {
  if (!source.body) throw new Error('서버 응답 본문이 없습니다.');
  if (Number(source.headers.get('content-length')) > maxBytes) {
    await source.body.cancel();
    throw new Error('응답 데이터가 허용된 크기를 초과했습니다.');
  }
  const reader = source.body.getReader();
  const decoder = new TextDecoder('utf-8', {fatal: true});
  let text = '';
  let count = 0;
  try {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      count += value.byteLength;
      if (count > maxBytes) {
        throw new Error('응답 데이터가 허용된 크기를 초과했습니다.');
      }
      text += decoder.decode(value, {stream: true});
    }
    return text + decoder.decode();
  } catch (error) {
    // UTF-8 오류·크기 초과·중단 때도 읽기 스트림을 정리하되 최초 오류를 유지합니다.
    await reader.cancel().catch(() => undefined);
    throw error;
  } finally {
    reader.releaseLock();
  }
}
export async function readJson(source: Request | Response, maxBytes = 2 * 1024 * 1024): Promise<unknown> {
  return JSON.parse(await readText(source, maxBytes)) as unknown;
}

// 실제 HTTP 요청은 이 함수 한 곳에서 실행합니다. 실패한 업무 요청을 자동 재전송하지 않습니다.
// signal은 cancel 방식에서만 전달하며, poll 방식에서는 fetch에 취소 신호 자체를 넣지 않습니다.
async function post(url: string, body: unknown, signal?: AbortSignal) {
  signal?.throwIfAborted();
  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body), cache: 'no-store', redirect: 'error',
      ...(signal ? { signal } : {}),
    });
  } catch (error) {
    // 시간 초과로 중단된 요청을 일반적인 연결 실패로 바꾸지 않습니다.
    if (signal?.aborted) throw error;
    throw new NetworkRequestError(error);
  }
  // 응답 본문을 읽는 중에도 fetch에 연결된 signal로 중단할 수 있습니다.
  let raw: unknown;
  try { raw = await readJson(response, 8 * 1024 * 1024); }
  catch (error) {
    if (!response.ok && !signal?.aborted) throw new TransportError(response.status);
    throw error;
  }
  if (!response.ok) {
    // HTTP 오류 응답에도 error_code/error_msg가 있으면 백엔드 메시지를 우선합니다.
    if (isObject(raw)) gatewayResponse(raw);
    throw new TransportError(response.status);
  }
  return raw;
}

// 폴링은 최초 업무 요청을 반복하는 것이 아니라, 같은 cid의 결과만 다시 조회하는 과정입니다.
async function pollResult(initial: unknown, fetchResult: (cid: string) => Promise<unknown>): Promise<unknown> {
  let raw = initial;
  const cid = isObject(raw) ? raw.cid : undefined;
  while (pending(raw)) {
    if (!validCid(cid)) throw new Error('결과 조회에 필요한 cid가 없거나 올바르지 않습니다.');
    if (isObject(raw) && raw.cid !== undefined && raw.cid !== cid) throw new Error('요청한 cid와 다른 결과가 반환되었습니다.');
    // Gateway가 wait_sec 동안 기다린 뒤 응답하므로, 응답 후 바로 다음 결과 조회를 보냅니다.
    // pending 응답에 cid가 생략되어도 최초에 받은 cid를 계속 사용합니다.
    raw = await fetchResult(cid);
  }
  gatewayResponse(raw); // error_code가 0이 아니면 error_msg로 예외를 만듭니다.
  if (cid !== undefined && isObject(raw) && raw.cid !== undefined && raw.cid !== cid) throw new Error('요청한 cid와 다른 결과가 반환되었습니다.');
  return raw;
}

// 결과 조회에는 원래 요청의 회사·캐시·대기 시간과 cid만 필요합니다.
function resultPacket(packet: Record<string, unknown>, cid: string) {
  return {
    case: 'result', cid, com_code: packet.com_code,
    cache_sec: packet.cache_sec ?? defaultCacheSeconds,
    wait_sec: packet.wait_sec ?? defaultWaitSeconds,
  };
}

// 최초 요청 1회 → accepted/pending이면 결과 조회 반복 → 최종 응답 반환.
async function requestResult(url: string, packet: Record<string, unknown>, waitMode?: GatewayWaitMode): Promise<unknown> {
  // cancel을 명시한 경우에만 취소 신호를 사용합니다. 생략·undefined는 poll입니다.
  if (waitMode !== 'cancel') {
    const initial = await post(url, packet);
    return pollResult(initial, (cid) => post(url, resultPacket(packet, cid)));
  }

  // cancel은 최초 요청부터 모든 후속 결과 조회까지 하나의 제한 시간을 공유합니다.
  // 매번 타이머를 새로 시작하면 pending이 계속 올 때 영원히 중단되지 않을 수 있습니다.
  const waitSeconds = packet.wait_sec ?? defaultWaitSeconds;
  if (typeof waitSeconds !== 'number' || !Number.isInteger(waitSeconds) || waitSeconds < 1 || waitSeconds > 60) {
    throw new Error('cancel 방식에서는 wait_sec를 1–60초 정수로 설정하세요.');
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), waitSeconds * 1000);
  try {
    const initial = await post(url, packet, controller.signal);
    const raw = await pollResult(initial, (cid) => post(url, resultPacket(packet, cid), controller.signal));
    controller.signal.throwIfAborted();
    return raw;
  } catch (error) {
    if (controller.signal.aborted) throw new GatewayTimeoutError(waitSeconds);
    throw error;
  } finally {
    // 성공·실패 모두 타이머를 정리해, 완료된 요청에 뒤늦은 취소가 발생하지 않게 합니다.
    clearTimeout(timer);
  }
}

// 암호화에 사용할 공개키도 Gateway의 work 요청으로 조회합니다.
// 공개키 요청과 상품 요청은 각각 별도의 대기 흐름이며, 같은 waitMode 정책을 적용합니다.
async function publicKeyPem(url: string, packet: Record<string, unknown>, waitMode?: GatewayWaitMode): Promise<{pem: string} | {response: unknown}> {
  const raw = await requestResult(url, {
    case: 'work', com_code: packet.com_code, c_code: packet.c_code,
    group: 'security', service: 'security', call: 'security',
    cache_sec: packet.cache_sec ?? defaultCacheSeconds,
    wait_sec: packet.wait_sec ?? defaultWaitSeconds,
    request_data: {},
  }, waitMode);
  const response = businessResponse(raw);
  // 공개키 조회의 업무 실패도 원래 ret_msg를 전달합니다. 상품 요청이나 평문 재전송을 진행하지 않습니다.
  if (response.code !== 0) return {response: raw};
  const value = response.result;
  const pem = isObject(value) ? value.public_key_pem ?? value.public_key : null;
  if (typeof pem !== 'string' || pem.length > 16384) throw new Error('Gateway 공개키를 확인할 수 없습니다. 암호화 설정을 확인하세요.');
  return {pem};
}

/**
 * 화면 → client.ts → gatewayRequest → work 요청 → cid로 result 조회 → 최종 응답 순서입니다.
 * encrypted는 request_data 암호화 여부, waitMode는 응답을 기다리는 정책입니다.
 * waitMode를 생략하거나 undefined로 전달하면 poll로 처리합니다.
 * poll은 강제 취소 없이 기다리며 wait_sec=0도 지원합니다.
 * cancel은 wait_sec(1–60초) 이후 AbortSignal로 응답 대기만 중단합니다. 서버 작업 취소 API는 아닙니다.
 */
export async function gatewayRequest(
  url: string, packet: Record<string, unknown>, encrypted: boolean, waitMode?: GatewayWaitMode,
): Promise<unknown> {
  // 1. 암호화를 켰다면 공개키를 가져와 request_data만 암호화합니다.
  let payload: Awaited<ReturnType<typeof encryptPayloadRequest>> | undefined;
  if (encrypted) {
    const key = await publicKeyPem(url, packet, waitMode);
    if ('response' in key) return key.response;
    payload = await encryptPayloadRequest(packet.request_data, await importPayloadPublicKey(key.pem));
  }
  const body = payload ? { ...packet, request_data: payload.envelope } : packet;

  // 2. 업무 요청은 한 번만 보냅니다. accepted/pending이면 같은 cid의 최종 결과를 기다립니다.
  const raw = await requestResult(url, body, waitMode);
  if (!payload) return raw;

  // 3. 최초 요청의 암호화 문맥으로 최종 응답을 복호화합니다.
  // 암호화 응답이 잘못되어도 평문으로 다시 요청하지 않습니다.
  const root = gatewayResponse(raw);
  if (!isObject(root) || !isPayloadEnvelope(root.response_data)) throw new Error('암호화된 응답이 필요합니다. Gateway의 암호화 설정을 확인하세요.');
  return { ...root, response_data: await decryptPayloadResponse(root.response_data, payload.context) };
}
