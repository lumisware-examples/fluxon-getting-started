import {ZodError} from 'zod';

// 서버 error_msg/ret_msg는 바꾸지 않습니다. 브라우저 자체 예외만 한국어 안내로 정리합니다.
export function getErrorMessage(error: unknown): string {
  if (error instanceof ZodError) {
    const message = error.issues[0]?.message;
    return message && /[가-힣]/.test(message) ? message : '입력값의 형식을 확인하세요.';
  }
  if (error instanceof SyntaxError) return '서버 응답의 JSON 형식이 올바르지 않습니다.';
  if (error instanceof DOMException) return '암호화 데이터를 처리할 수 없습니다. Gateway 설정을 확인하세요.';
  if (error instanceof TypeError) return '응답 데이터를 처리할 수 없습니다. 데이터 형식을 확인하세요.';
  return error instanceof Error ? error.message : '요청 처리 중 오류가 발생했습니다.';
}
