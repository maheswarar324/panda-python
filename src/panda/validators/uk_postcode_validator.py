import re


def is_valid_uk_postcode(value: str) -> bool:
    if not isinstance(value, str):
        return False

    value = value.strip().upper()

    pattern = r"[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}"

    return re.fullmatch(pattern, value) is not None
