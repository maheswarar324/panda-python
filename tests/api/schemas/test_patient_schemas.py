from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from panda.api.schemas.patient_schemas import (
    PatientCreate,
    PatientPostcodeUpdate,
    PatientResponse,
)

# --------------------------------------------------
# PatientCreate tests
# --------------------------------------------------


def test_patient_create_with_valid_data() -> None:
    patient = PatientCreate(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth="1990-05-15",
        postcode="SW1A 1AA",
    )

    assert patient.nhs_number == "9434765919"
    assert patient.first_name == "John"
    assert patient.last_name == "Smith"
    assert patient.date_of_birth == date(1990, 5, 15)
    assert patient.postcode == "SW1A 1AA"


def test_patient_create_rejects_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        PatientCreate(
            nhs_number="9434765919",
            first_name="John",
            last_name="Smith",
            date_of_birth="1990-05-15",
        )


def test_patient_create_rejects_invalid_date() -> None:
    with pytest.raises(ValidationError):
        PatientCreate(
            nhs_number="9434765919",
            first_name="John",
            last_name="Smith",
            date_of_birth="invalid-date",
            postcode="SW1A 1AA",
        )


def test_patient_create_rejects_invalid_date_format() -> None:
    with pytest.raises(ValidationError):
        PatientCreate(
            nhs_number="9434765919",
            first_name="John",
            last_name="Smith",
            date_of_birth="15-05-1990",
            postcode="SW1A 1AA",
        )


def test_patient_create_rejects_invalid_field_types() -> None:
    with pytest.raises(ValidationError):
        PatientCreate(
            nhs_number=1234567890,
            first_name="John",
            last_name="Smith",
            date_of_birth="1990-05-15",
            postcode="SW1A 1AA",
        )


# --------------------------------------------------
# PatientResponse tests
# --------------------------------------------------


def test_patient_response_with_valid_data() -> None:
    patient = PatientResponse(
        id=1,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth="1990-05-15",
        postcode="SW1A 1AA",
    )

    assert patient.id == 1
    assert patient.nhs_number == "9434765919"
    assert patient.first_name == "John"
    assert patient.last_name == "Smith"
    assert patient.date_of_birth == date(1990, 5, 15)
    assert patient.postcode == "SW1A 1AA"


def test_patient_response_from_domain_object() -> None:
    patient = SimpleNamespace(
        id=1,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 15),
        postcode="SW1A 1AA",
    )

    response = PatientResponse.model_validate(patient)

    assert response.id == 1
    assert response.nhs_number == "9434765919"
    assert response.first_name == "John"
    assert response.last_name == "Smith"
    assert response.date_of_birth == date(1990, 5, 15)
    assert response.postcode == "SW1A 1AA"


def test_patient_response_rejects_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        PatientResponse(
            id=1,
            nhs_number="9434765919",
            first_name="John",
            last_name="Smith",
            date_of_birth="1990-05-15",
        )


def test_patient_response_rejects_invalid_id() -> None:
    with pytest.raises(ValidationError):
        PatientResponse(
            id="invalid",
            nhs_number="9434765919",
            first_name="John",
            last_name="Smith",
            date_of_birth="1990-05-15",
            postcode="SW1A 1AA",
        )


# --------------------------------------------------
# PatientPostcodeUpdate tests
# --------------------------------------------------


def test_patient_postcode_update_with_valid_data() -> None:
    update = PatientPostcodeUpdate(postcode="M1 1AE")

    assert update.postcode == "M1 1AE"


def test_patient_postcode_update_rejects_missing_postcode() -> None:
    with pytest.raises(ValidationError):
        PatientPostcodeUpdate()


def test_patient_postcode_update_rejects_invalid_field_type() -> None:
    with pytest.raises(ValidationError):
        PatientPostcodeUpdate(postcode=12345)
