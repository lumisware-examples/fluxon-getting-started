#!/bin/bash

# 도커 내 서비스 이름
Docker_Name="fluxon-demo-worker-fluxondemo-v10"


# Docker 컨테이너 내부 tester.py 경로
Tester_FPath="/app/tester.py"

print_usage() {
    echo "사용법"
    echo "  $0 [request_name] [test|deploy]"
    echo "  $0 com_build [그룹명[/서비스명]] 모듈명"
    echo
    echo "업무 모듈 test/deploy 예"
    echo "  $0 ApplicationExample          # 기본 동작은 test"
    echo "  $0 ApplicationExample test     # Python 업무 모듈 실행 테스트"
    echo "  $0 ApplicationExample deploy   # 업무 모듈을 빌드해 exec에 저장"
    echo
    echo "공통 모듈 빌드 예"
    echo "  $0 com_build  그룹명/서비스명  모듈명   # 서비스 범위"
    echo "  $0 com_build  그룹명  모듈명          # 그룹 범위"
    echo "  $0 com_build  모듈명                # 회사코드 범위"
    echo "  회사코드는 컨테이너에서 읽고, 지정한 범위 아래의 svc_common을 사용합니다."
    echo "  모듈명에 .py를 생략하면 자동으로 붙입니다. AMD64·ARM64 .so는 원본 옆에 저장합니다."
}

# -----------------------------------------------------------------------------
# 공통 모듈 빌드: com_build [그룹명[/서비스명]] 모듈명
# JSON 없이 컨테이너의 com_code를 기준으로 svc_common 모듈을 빌드한다.
# -----------------------------------------------------------------------------
if [ "${1:-}" = "com_build" ]; then
    if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
        echo "[ERROR] com_build에는 모듈명과 선택 범위(그룹명 또는 그룹명/서비스명)를 지정합니다."
        print_usage
        exit 1
    fi

    CommonScope=""
    ModuleFile="$2"
    if [ "$#" -eq 3 ]; then
        case "$2" in
            ""|/*|*/|*/*/*)
                echo "[ERROR] 범위는 그룹명 또는 그룹명/서비스명 형식이어야 합니다."
                print_usage
                exit 1
                ;;
        esac
        CommonScope="$2/"
        ModuleFile="$3"
    fi
    if [[ -z "$ModuleFile" || "$ModuleFile" == .py || "$ModuleFile" == */* ]]; then
        echo "[ERROR] 모듈은 경로 없이 이름만 지정합니다. .py 확장자는 생략할 수 있습니다."
        print_usage
        exit 1
    fi
    if [[ "$ModuleFile" != *.py ]]; then
        ModuleFile+=".py"
    fi
    CommonPath="${CommonScope}svc_common/$ModuleFile"

    if ! docker inspect -f '{{.State.Running}}' "$Docker_Name" 2>/dev/null \
        | grep -q '^true$'; then
        echo "[ERROR] Docker 컨테이너가 실행 중이 아닙니다: $Docker_Name"
        exit 1
    fi

    # 회사 코드를 중복 설정하지 않고 대상 worker의 환경 변수에서 읽는다.
    ComCode="$(docker exec "$Docker_Name" printenv com_code)"
    if [ "$?" -ne 0 ] || [ -z "$ComCode" ]; then
        echo "[ERROR] 컨테이너의 com_code 환경 변수를 읽을 수 없습니다: $Docker_Name"
        exit 1
    fi

    echo "[INFO] 공통 모듈 빌드: /app/modules/$ComCode/$CommonPath"
    docker exec "$Docker_Name" \
        python "$Tester_FPath" com_build "$ComCode/$CommonPath"
    Result=$?
    if [ "$Result" -ne 0 ]; then
        echo "[ERROR] 공통 모듈 빌드 실패 (종료 코드: $Result)"
        exit "$Result"
    fi
    echo "[INFO] 공통 모듈 빌드가 완료되었습니다."
    exit 0
fi

# -----------------------------------------------------------------------------
# 입력 파라미터
# -----------------------------------------------------------------------------
RequestName="$1"   # JSON 파일명 및 요청명(.json 제외)
Option="$2"        # deploy 또는 test 또는 생략

if [ -z "$RequestName" ]; then
    echo "[ERROR] 첫 번째 파라미터로 Class명(요청명)을 입력해야 합니다."
    print_usage
    exit 1
fi

if [ "$#" -gt 2 ] || { [ -n "$Option" ] && [ "$Option" != "deploy" ] && [ "$Option" != "test" ]; }; then
    echo "[ERROR] 업무 모듈 명령은 요청명과 선택 옵션(deploy 또는 test)만 받습니다."
    print_usage
    exit 1
fi

# -----------------------------------------------------------------------------
# 현재 쉘 스크립트가 위치한 디렉터리
# -----------------------------------------------------------------------------
Script_Dir="$PWD"

# -----------------------------------------------------------------------------
# JSON 파일 검색
#
# 우선순위:
#   1. 하위 src 폴더
#   2. 하위 test 폴더
# -----------------------------------------------------------------------------
JsonFile="$(find "$Script_Dir" -type f \
    -path "*/src/${RequestName}.json" \
    -print -quit 2>/dev/null)"

if [ -z "$JsonFile" ]; then
    JsonFile="$(find "$Script_Dir" -type f \
        -path "*/test/${RequestName}.json" \
        -print -quit 2>/dev/null)"
fi

if [ -z "$JsonFile" ]; then
    echo "[ERROR] '${RequestName}.json' 파일을 찾을 수 없습니다."
    echo "[INFO] 검색 기준 경로: $Script_Dir"
    echo "[INFO] 검색 대상:"
    echo "       */src/${RequestName}.json"
    echo "       */test/${RequestName}.json"
    exit 1
fi

echo "[INFO] JSON 파일: $JsonFile"

# -----------------------------------------------------------------------------
# JSON 파일에서 com_code, group, service 읽기
#
# JSON 파싱 결과를 탭 문자로 구분하여 한 줄로 반환
# -----------------------------------------------------------------------------
JsonValues="$(
python3 - "$JsonFile" <<'PY'
import json
import sys

json_file = sys.argv[1]

try:
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"[ERROR] JSON 파일이 없습니다: {json_file}", file=sys.stderr)
    sys.exit(1)
except PermissionError:
    print(f"[ERROR] JSON 파일을 읽을 권한이 없습니다: {json_file}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as exc:
    print(
        f"[ERROR] JSON 형식이 올바르지 않습니다: "
        f"line={exc.lineno}, column={exc.colno}, message={exc.msg}",
        file=sys.stderr,
    )
    sys.exit(1)
except OSError as exc:
    print(f"[ERROR] JSON 파일 읽기 실패: {exc}", file=sys.stderr)
    sys.exit(1)

required_fields = (
    "com_code",
    "group",
    "service",
)

values = []

for field in required_fields:
    value = data.get(field)

    if value is None or str(value).strip() == "":
        print(
            f"[ERROR] JSON 필수 필드가 없거나 비어 있습니다: {field}",
            file=sys.stderr,
        )
        sys.exit(1)

    values.append(str(value).strip())

print("\t".join(values))
PY
)"

PythonResult=$?

if [ "$PythonResult" -ne 0 ]; then
    exit 1
fi

# 탭으로 구분된 값 분리
IFS="$(printf '\t')" read -r ComCode GroupName ServiceName <<EOF
$JsonValues
EOF

if [ -z "$ComCode" ] || [ -z "$GroupName" ] || [ -z "$ServiceName" ]; then
    echo "[ERROR] JSON에서 필수 값을 읽지 못했습니다."
    echo "[INFO] com_code : $ComCode"
    echo "[INFO] group    : $GroupName"
    echo "[INFO] service  : $ServiceName"
    exit 1
fi

echo "[INFO] com_code : $ComCode"
echo "[INFO] group    : $GroupName"
echo "[INFO] service  : $ServiceName"
echo "[INFO] request  : $RequestName"

# -----------------------------------------------------------------------------
# Docker 컨테이너 실행 여부 확인
# -----------------------------------------------------------------------------
if ! docker inspect -f '{{.State.Running}}' "$Docker_Name" 2>/dev/null \
    | grep -q '^true$'; then
    echo "[ERROR] Docker 컨테이너가 실행 중이 아닙니다: $Docker_Name"
    exit 1
fi

# -----------------------------------------------------------------------------
# tester.py 실행
# -----------------------------------------------------------------------------
if [ "$Option" = "deploy" ]; then
    echo "[INFO] '$RequestName' 모듈을 deploy 모드로 실행합니다."

    docker exec "$Docker_Name" \
        python "$Tester_FPath" \
        "$ComCode" \
        "$GroupName" \
        "$ServiceName" \
        "$RequestName" \
        deploy
else
    echo "[INFO] '$RequestName' 모듈을 일반 모드로 실행합니다."

    docker exec "$Docker_Name" \
        python "$Tester_FPath" \
        "$ComCode" \
        "$GroupName" \
        "$ServiceName" \
        "$RequestName"
fi

Result=$?

echo

if [ "$Result" -ne 0 ]; then
    echo "[ERROR] tester.py 실행 중 오류가 발생했습니다."
    echo "[INFO] 종료 코드: $Result"
    exit "$Result"
fi

echo "[INFO] 실행이 완료되었습니다."
exit 0
