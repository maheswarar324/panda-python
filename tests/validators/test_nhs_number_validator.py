import pytest

from panda.validators.nhs_number_validator import is_valid_nhs_number

# def test_valid_nhs_number():
#     assert is_valid_nhs_number("9434765919") is True

# def test_nhs_number_with_too_few_digits():
#     assert is_valid_nhs_number("123456789") is False


# def test_nhs_number_with_letters():
#     assert is_valid_nhs_number("123456789A") is False


# def test_nhs_number_with_invalid_checksum():
#     assert is_valid_nhs_number("9434765918") is False


@pytest.mark.parametrize(
    "nhs_number",
    [
        "123",
        "ABCDEFGHIJ",
        "",
        "12345678901",
        "12345ABCDE",
    ],
)
def test_invalid_nhs_numbers(nhs_number):
    assert is_valid_nhs_number(nhs_number) is False
