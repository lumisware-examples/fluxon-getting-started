import math
import re


# Fluxon의 DB 스키마 이름과 세션을 반환
def get_mysql_context(job, db_name="MySQL"):
    """DB 스키마 이름과 세션을 반환한다."""
    schema_name = job.FLX_Get_Property_Default_StorageName # schema_name = fluxondemo
    db_session = job.FLX_MySql_Get_Session(db_name)

    return schema_name, db_session


# 2026.11.09: 등록·수정이 공유하는 상품 입력 검증을 추가.
def validate_product_values(data) -> tuple[dict[str, str | int] | None, int, str]:
    """저장할 값·ret_code·ret_msg를 반환한다. 실패 시 저장할 값은 None이다."""
    name = data.get("name")
    category = data.get("category")
    price = data.get("price")

    if not isinstance(name, str):
        return None, 11, "상품명을 입력하세요."
    # JavaScript의 trim()과 같은 공백을 제거합니다(BOM도 포함).
    name = name.strip("\t\n\v\f\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005"
                      "\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff")
    if not name:
        return None, 11, "상품명을 입력하세요."
    # JavaScript 문자열 길이는 UTF-16 기준이므로 이모지도 프런트엔드와 동일하게 셉니다.
    if len(name.encode("utf-16-le", errors="surrogatepass")) // 2 > 80:
        return None, 12, "상품명은 80자 이하로 입력하세요."

    if not isinstance(category, str) or not re.fullmatch(r"[A-Z_]{1,40}", category):
        return None, 13, "상품 분류는 영문 대문자와 밑줄로 1–40자 입력하세요."

    # bool은 Python에서는 int의 하위 타입이지만, 프런트엔드에서는 숫자가 아니므로 제외합니다.
    if type(price) not in (int, float) or (type(price) is float and not math.isfinite(price)):
        return None, 14, "가격을 입력하세요."
    # JSON의 1000.0도 숫자 1000과 같게 취급하며, 실제 소수 값은 거부합니다.
    if type(price) is float and not price.is_integer():
        return None, 15, "가격은 정수로 입력하세요."
    if price < 0:
        return None, 16, "가격은 0 이상이어야 합니다."
    if price > 2147483647:
        return None, 17, "가격이 저장 가능한 범위를 넘었습니다."

    return {"name": name, "category": category, "price": int(price)}, 0, ""


def validate_product_id(product_id) -> tuple[int | None, int, str]:
    """ID는 양의 정수만 허용한다. bool·소수·숫자 문자열을 자동 변환하지 않는다."""
    if type(product_id) is not int or not 1 <= product_id <= 2147483647:
        return None, 18, "상품 ID는 1–2147483647 사이의 정수여야 합니다."
    return product_id, 0, ""
