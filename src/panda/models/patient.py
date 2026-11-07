from dataclasses import dataclass
from datetime import date

from panda.validators.nhs_number_validator import is_valid_nhs_number
from panda.validators.uk_postcode_validator import is_valid_uk_postcode


@dataclass
class Patient:
    id: (
        int | None
    )  # int | None means the ID can be an integer or None. A new patient can have id=None until the database assigns an ID.
    nhs_number: str
    first_name: str
    last_name: str
    date_of_birth: date  # date represents a calendar date without a time, matching Java's LocalDate.
    postcode: str

    def __post_init__(self) -> None:
        if not is_valid_nhs_number(self.nhs_number):
            raise ValueError("Invalid NHS number")

        if not is_valid_uk_postcode(self.postcode):
            raise ValueError("Invalid UK postcode")
