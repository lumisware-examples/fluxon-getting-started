// 예제 목록은 백엔드 demo_group/examples/test의 요청 JSON과 맞춥니다.
// 이 파일은 화면에 표시할 설명과 입력 예시만 정의하며 Gateway를 호출하지 않습니다.
export type ExampleCall = 'ExampleMysqlSetup' | 'ExampleEcho' | 'ExampleValidation' | 'ExampleTypeConversion' | 'ExampleResponse' | 'ExampleConfig' | 'ExampleCommon' | 'ExampleMySqlSelect' | 'ExampleMySqlInsert' | 'ExampleMySqlUpdate' | 'ExampleMySqlDelete' | 'ExampleTransaction' | 'ExampleDelayedResult';

export type ExamplePreset = {label: string; input: Record<string, unknown>; country?: string};
export type ExampleDefinition = {
  call: ExampleCall;
  label: string;
  description: string;
  hint: string;
  needsDatabase: boolean;
  defaultInput: Record<string, unknown>;
  presets: readonly ExamplePreset[];
};

export const EXAMPLES: readonly ExampleDefinition[] = [
  {
    "call": "ExampleMysqlSetup",
    "label": "MySQL 준비 · ExampleMysqlSetup",
    "description": "실습 테이블을 준비합니다.",
    "hint": "CREATE TABLE IF NOT EXISTS를 사용하며 반복 실행해도 기존 행과 ID를 유지합니다.",
    "needsDatabase": true,
    "defaultInput": {},
    "presets": []
  },
  {
    "call": "ExampleEcho",
    "label": "01. 메시지 반환 · ExampleEcho",
    "description": "보낸 메시지를 그대로 돌려받습니다.",
    "hint": "공백과 줄바꿈을 유지합니다. 빈 메시지를 보내 업무 실패도 확인해 보세요.",
    "needsDatabase": false,
    "defaultInput": {
      "message_1": "안녕하세요, Fluxon!",
      "message_2": "메시지 반환 테스트입니다."
    },
    "presets": [
      {
        "label": "빈 메시지 입력",
        "input": {
          "message_1": "   "
        }
      }
    ]
  },
  {
    "call": "ExampleValidation",
    "label": "02. 입력 검증 · ExampleValidation",
    "description": "필수 키 검사와 업무 값 검사를 비교합니다.",
    "hint": "quantity 키 누락은 Gateway 오류, 수량 범위 오류는 업무 ret_code로 반환합니다.",
    "needsDatabase": false,
    "defaultInput": {
      "name": "입문자",
      "quantity": 2
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "name": "입문자",
          "quantity": 0
        }
      },
      {
        "label": "필수값 누락 입력",
        "input": {
          "name": "입문자"
        }
      }
    ]
  },
  {
    "call": "ExampleTypeConversion",
    "label": "03. 타입 변환 · ExampleTypeConversion",
    "description": "문자열을 숫자와 불리언으로 바꿉니다.",
    "hint": "입력 JSON의 따옴표가 있는 숫자와 수신 결과의 숫자 타입을 비교하세요.",
    "needsDatabase": false,
    "defaultInput": {
      "quantity": "2",
      "enabled": "true",
      "unit_price": "1000"
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "quantity": "숫자 아님",
          "enabled": "true",
          "unit_price": "1000"
        }
      }
    ]
  },
  {
    "call": "ExampleResponse",
    "label": "04. 응답과 메시지 · ExampleResponse",
    "description": "성공·업무 실패와 국가별 메시지를 비교합니다.",
    "hint": "응답 메시지 언어를 영어로 바꾸거나 실패 입력을 선택해 확인하세요.",
    "needsDatabase": false,
    "defaultInput": {
      "outcome": "success",
      "name": "입문자"
    },
    "presets": [
      {
        "label": "업무 실패 입력",
        "input": {
          "outcome": "failure"
        }
      },
      {
        "label": "영어 응답 입력",
        "input": {
          "name": "Beginner"
        },
        "country": "USA"
      }
    ]
  },
  {
    "call": "ExampleConfig",
    "label": "05. 설정 읽기 · ExampleConfig",
    "description": "svc_info에서 공개 실습 설정을 읽습니다.",
    "hint": "입력값 없이 실행합니다. 개인키나 비밀번호가 아닌 공개 항목만 반환합니다.",
    "needsDatabase": false,
    "defaultInput": {},
    "presets": []
  },
  {
    "call": "ExampleCommon",
    "label": "06. 공통 함수 · ExampleCommon",
    "description": "공통 함수와 객체를 사용해 합계를 계산합니다.",
    "hint": "단가와 수량을 바꿔 반환된 total을 확인하세요.",
    "needsDatabase": false,
    "defaultInput": {
      "unit_price": 1000,
      "quantity": 2
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "unit_price": -1,
          "quantity": 2
        }
      }
    ]
  },
  {
    "call": "ExampleMySqlSelect",
    "label": "07. MySQL 조회 · ExampleMySqlSelect",
    "description": "목록·단건·개수 조회의 결과를 비교합니다.",
    "hint": "items는 목록, item은 해당 ID 한 건, total은 전체 개수입니다. 빈 결과도 정상입니다.",
    "needsDatabase": true,
    "defaultInput": {
      "id": 1,
      "limit": 10
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "limit": 0
        }
      }
    ]
  },
  {
    "call": "ExampleMySqlInsert",
    "label": "08. MySQL 등록 · ExampleMySqlInsert",
    "description": "실습 데이터를 저장하고 DB가 발급한 ID를 받습니다.",
    "hint": "수신 JSON의 result.id를 기록해 수정·삭제 입력의 id로 사용하세요.",
    "needsDatabase": true,
    "defaultInput": {
      "name": "실습 노트",
      "price": 1000
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "name": "실습",
          "price": -1
        }
      }
    ]
  },
  {
    "call": "ExampleMySqlUpdate",
    "label": "09. MySQL 수정 · ExampleMySqlUpdate",
    "description": "ID로 지정한 실습 데이터의 이름과 가격을 바꿉니다.",
    "hint": "실제로 등록된 ID를 입력하세요. 대상이 없으면 업무 실패 메시지를 반환합니다.",
    "needsDatabase": true,
    "defaultInput": {
      "id": 1,
      "name": "수정한 실습 노트",
      "price": 2000
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "id": 0,
          "name": "실습",
          "price": 1000
        }
      }
    ]
  },
  {
    "call": "ExampleMySqlDelete",
    "label": "10. MySQL 삭제 · ExampleMySqlDelete",
    "description": "지정한 ID의 실습 데이터 한 건을 삭제합니다.",
    "hint": "삭제할 실습 데이터의 ID를 확인하고 실행하세요.",
    "needsDatabase": true,
    "defaultInput": {
      "id": 6
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "id": 0
        }
      }
    ]
  },
  {
    "call": "ExampleTransaction",
    "label": "11. 트랜잭션 · ExampleTransaction",
    "description": "두 등록을 함께 확정하거나 함께 취소합니다.",
    "hint": "기본 입력은 두 행을 저장합니다. 롤백 입력은 두 등록을 모두 취소하고 기존 행을 유지합니다.",
    "needsDatabase": true,
    "defaultInput": {
      "simulate_failure": false
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "simulate_failure": "true"
        }
      },
      {
        "label": "롤백 입력",
        "input": {
          "simulate_failure": true
        }
      }
    ]
  },
  {
    "call": "ExampleDelayedResult",
    "label": "12. 지연 처리와 폴링 · ExampleDelayedResult",
    "description": "잠시 기다린 뒤 최종 응답을 확인합니다.",
    "hint": "이 예제는 wait_sec=1로 요청합니다. accepted/pending이면 같은 cid로 결과만 조회합니다.",
    "needsDatabase": false,
    "defaultInput": {
      "delay_sec": 3
    },
    "presets": [
      {
        "label": "잘못된 입력",
        "input": {
          "delay_sec": 0
        }
      }
    ]
  }
];
