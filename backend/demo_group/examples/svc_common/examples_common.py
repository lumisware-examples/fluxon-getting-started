"""examples 서비스 안에서만 쓰는 작은 공통 함수입니다. 기존 상품 예제와 독립적입니다."""
import re

CURRENCY = "KRW"


def calculate_total(unit_price, quantity):
    """단가와 수량을 곱합니다. 호출한 워크 모듈에서 입력을 먼저 검사합니다."""
    return unit_price * quantity


def get_mysql_context(job):
    # 스키마 이름은 사용자 입력이 아니라 워커의 기본 저장소 설정을 사용합니다.
    schema_name = job.FLX_Get_Property_Default_StorageName
    if not isinstance(schema_name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", schema_name):
        schema_name = "fluxondemo"
    return schema_name, job.FLX_MySql_Get_Session("MySQL")


def validate_item(data):
    """DB에 저장할 값 또는 업무 실패 코드를 반환합니다. 검증 실패 때는 DB에 접근하지 않습니다."""
    name, price = data.get("name"), data.get("price")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80:
        return None, 11, "이름은 공백을 제외하고 1–80자로 입력하세요."
    if type(price) is not int or not 0 <= price <= 2147483647:
        return None, 12, "가격은 0–2147483647의 정수로 입력하세요."
    return {"name": name.strip(), "price": price}, 0, ""


def valid_id(value):
    return type(value) is int and 1 <= value <= 2147483647
