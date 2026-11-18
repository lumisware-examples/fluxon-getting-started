"""demo_group 안에서만 쓰는 공통 함수입니다."""


def calculate_total(unit_price, quantity):
    """단가와 수량을 곱합니다. 호출한 워크 모듈에서 입력을 먼저 검사합니다."""
    return unit_price * quantity
