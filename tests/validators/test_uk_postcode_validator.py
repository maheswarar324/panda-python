from panda.validators.uk_postcode_validator import is_valid_uk_postcode


def test_valid_uk_postcode():
    assert is_valid_uk_postcode("SW1A 1AA") is True


def test_lowercase_postcode():
    assert is_valid_uk_postcode("sw1a 1aa") is True


def test_postcode_with_surrounding_spaces():
    assert is_valid_uk_postcode("  SW1A 1AA  ") is True
