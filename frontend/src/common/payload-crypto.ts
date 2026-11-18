// Gateway와 공유하는 암호화 전송 형식입니다. GCM 인증 태그는 암호문 끝에 붙습니다.
// 처음에는 호출 흐름만 읽고, 암호화 세부 구현은 docs/BEGINNER_GUIDE.md의 심화 순서로 살펴보세요.
const encoder = new TextEncoder();
const decoder = new TextDecoder();

export type PayloadEnvelope = {
  secure: true;
  protected: string;
  encrypted_key?: string;
  iv: string;
  ciphertext: string;
};

export type PayloadContext = { aesKey: CryptoKey; nonce: string };
export type PayloadBinding = {
  method: string;
  path: string;
  kid: string;
  status?: number;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

export const isPayloadEnvelope = (value: unknown): value is PayloadEnvelope =>
  isRecord(value) &&
  value.secure === true &&
  typeof value.protected === "string" &&
  typeof value.iv === "string" &&
  typeof value.ciphertext === "string";

export const encode64 = (bytes: Uint8Array): string => {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
};

export const decode64 = (value: string): Uint8Array<ArrayBuffer> => {
  if (!value || !/^[A-Za-z0-9_+/=-]+$/.test(value))
    throw new Error("암호화 데이터의 Base64 형식이 올바르지 않습니다.");
  return Uint8Array.from(
    atob(value.replace(/-/g, "+").replace(/_/g, "/")),
    (c) => c.charCodeAt(0),
  );
};

export async function importPayloadPublicKey(pem: string): Promise<CryptoKey> {
  const bytes = decode64(
    pem.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\s/g, ""),
  );
  const key = await crypto.subtle.importKey(
    "spki",
    bytes,
    { name: "RSA-OAEP", hash: "SHA-256" },
    false,
    ["encrypt"],
  );
  if ((key.algorithm as RsaHashedKeyAlgorithm).modulusLength < 2048)
    throw new Error("공개키의 RSA 길이가 2048비트보다 짧습니다.");
  return key;
}

export function readPayloadHeader(
  envelope: PayloadEnvelope,
  type: "request" | "response",
): Record<string, unknown> {
  const header: unknown = JSON.parse(
    decoder.decode(decode64(envelope.protected)),
  );
  if (
    !isRecord(header) ||
    header.v !== 1 ||
    header.typ !== type ||
    header.alg !== "RSA-OAEP-256" ||
    header.enc !== "A256GCM" ||
    typeof header.nonce !== "string" ||
    decode64(header.nonce).length !== 16 ||
    !Number.isSafeInteger(header.timestamp)
  )
    throw new Error("암호화 데이터의 헤더가 올바르지 않습니다.");
  return header;
}

const verifyBinding = (
  header: Record<string, unknown>,
  binding?: PayloadBinding,
) => {
  if (
    binding &&
    Object.entries(binding).some(([key, value]) => header[key] !== value)
  ) {
    throw new Error("암호화 데이터의 요청 정보가 일치하지 않습니다.");
  }
};

async function seal(
  data: unknown,
  context: PayloadContext,
  type: "request" | "response",
  binding?: PayloadBinding,
): Promise<PayloadEnvelope> {
  const protectedHeader = encode64(
    encoder.encode(
      JSON.stringify({
        alg: "RSA-OAEP-256",
        enc: "A256GCM",
        nonce: context.nonce,
        timestamp: Math.floor(Date.now() / 1000),
        typ: type,
        v: 1,
        ...binding,
      }),
    ),
  );
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv, additionalData: encoder.encode(protectedHeader) },
    context.aesKey,
    encoder.encode(JSON.stringify(data)),
  );
  return {
    secure: true,
    protected: protectedHeader,
    iv: encode64(iv),
    ciphertext: encode64(new Uint8Array(ciphertext)),
  };
}

// 요청마다 새 AES 키·nonce를 만듭니다. AES 키는 Gateway의 RSA 공개키로 감싸서 전달합니다.
export async function encryptPayloadRequest(
  data: unknown,
  publicKey: CryptoKey,
  binding?: PayloadBinding,
) {
  const aesKey = await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"],
  );
  const context = {
    aesKey,
    nonce: encode64(crypto.getRandomValues(new Uint8Array(16))),
  };
  const envelope = await seal(data, context, "request", binding);
  const encryptedKey = await crypto.subtle.encrypt(
    { name: "RSA-OAEP" },
    publicKey,
    await crypto.subtle.exportKey("raw", aesKey),
  );
  envelope.encrypted_key = encode64(new Uint8Array(encryptedKey));
  return { envelope, context };
}

// 요청 때 보관한 AES 키로 응답을 복호화합니다. GCM 검증 실패는 예외로 전달됩니다.
async function open(
  envelope: PayloadEnvelope,
  context: PayloadContext,
): Promise<unknown> {
  const iv = decode64(envelope.iv);
  if (iv.length !== 12) throw new Error("암호화 데이터의 초기화 벡터(IV)가 올바르지 않습니다.");
  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv, additionalData: encoder.encode(envelope.protected) },
    context.aesKey,
    decode64(envelope.ciphertext),
  );
  return JSON.parse(decoder.decode(plaintext)) as unknown;
}

export async function decryptPayloadRequest(
  envelope: PayloadEnvelope,
  privateKey: CryptoKey,
  binding: PayloadBinding,
) {
  const header = readPayloadHeader(envelope, "request");
  verifyBinding(header, binding);
  if (Math.abs(Date.now() / 1000 - Number(header.timestamp)) > 300)
    throw new Error("암호화 요청의 유효 시간이 지났습니다.");
  if (typeof envelope.encrypted_key !== "string")
    throw new Error("암호화된 키가 없습니다.");
  const rawKey = await crypto.subtle.decrypt(
    { name: "RSA-OAEP" },
    privateKey,
    decode64(envelope.encrypted_key),
  );
  if (rawKey.byteLength !== 32) throw new Error("AES 키의 크기가 올바르지 않습니다.");
  const aesKey = await crypto.subtle.importKey(
    "raw",
    rawKey,
    "AES-GCM",
    false,
    ["encrypt", "decrypt"],
  );
  const context = { aesKey, nonce: String(header.nonce) };
  return { data: await open(envelope, context), context };
}

export const encryptPayloadResponse = (
  data: unknown,
  context: PayloadContext,
  binding?: PayloadBinding,
) => seal(data, context, "response", binding);

export async function decryptPayloadResponse(
  envelope: PayloadEnvelope,
  context: PayloadContext,
  binding?: PayloadBinding,
) {
  const header = readPayloadHeader(envelope, "response");
  verifyBinding(header, binding);
  if (header.nonce !== context.nonce)
    throw new Error("응답 nonce가 요청과 일치하지 않습니다.");
  return open(envelope, context);
}
