from datetime import date

import pytest

from panda.models.patient import Patient


def test_patient_creation():
    patient = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    assert patient.id is None
    assert patient.first_name == "John"
    assert patient.last_name == "Smith"
    assert patient.date_of_birth == date(1990, 5, 20)


def test_patient_rejects_invalid_nhs_number():
    with pytest.raises(ValueError, match="Invalid NHS number"):
        Patient(
            id=None,
            nhs_number="123",
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 5, 20),
            postcode="SW1A 1AA",
        )


@pytest.mark.parametrize(
    "postcode",
    [
        "INVALID",
        "",
        "12345",
        "ABCDE",
    ],
)
def test_patient_rejects_invalid_postcode(postcode):
    with pytest.raises(ValueError, match="Invalid UK postcode"):
        Patient(
            id=None,
            nhs_number="9434765919",
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 5, 20),
            postcode=postcode,
        )
