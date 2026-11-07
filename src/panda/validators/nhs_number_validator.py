import re


def is_valid_nhs_number(value: str) -> bool:
    if not isinstance(value, str):
        return False

    # re.fullmatch(r"[0-9]{10}", value) vs re.fullmatch(r"\d{10}", value)
    # Yes. Both of these are valid:
    # There is a subtle difference: in Python, \d also matches certain Unicode digits, whereas [0-9] matches only ASCII digits (0–9) by default.
    if re.fullmatch(r"[0-9]{10}", value) is None:
        return False

    digits = [int(digit) for digit in value]

    weighted_sum = sum(
        digit * weight for digit, weight in zip(digits[:9], range(10, 1, -1))
    )

    check_digit = 11 - (weighted_sum % 11)

    if check_digit == 11:
        check_digit = 0
    if check_digit == 10:
        return False

    return check_digit == digits[9]
