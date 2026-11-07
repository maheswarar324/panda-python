from datetime import date

import pytest

from panda.models.patient import Patient
from panda.repositories.patient_repository import PatientRepository


def test_save_patient_assigns_id():
    repository = PatientRepository()

    patient = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    saved_patient = repository.save(patient)

    assert saved_patient.id == 1
    assert repository.find_by_id(1) is patient


def test_find_by_id_returns_none_when_not_found():
    repository = PatientRepository()

    assert repository.find_by_id(999) is None


def test_find_by_nhs_number_returns_patient():
    repository = PatientRepository()

    patient = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    repository.save(patient)

    assert repository.find_by_nhs_number("9434765919") is patient


def test_find_by_nhs_number_returns_none_when_not_found():
    repository = PatientRepository()

    assert repository.find_by_nhs_number("9434765919") is None


def test_save_rejects_duplicate_nhs_number():
    repository = PatientRepository()

    patient1 = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    patient2 = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1992, 3, 15),
        postcode="SW1A 1AA",
    )

    repository.save(patient1)

    with pytest.raises(ValueError, match="already exists"):
        repository.save(patient2)


def test_update_patient():
    repository = PatientRepository()

    patient = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    saved_patient = repository.save(patient)
    saved_patient.postcode = "SW1A 2AA"

    updated_patient = repository.update(saved_patient)

    assert updated_patient.postcode == "SW1A 2AA"
    assert repository.find_by_id(saved_patient.id) is updated_patient


def test_update_patient_raises_error_when_patient_not_found():
    repository = PatientRepository()

    patient = Patient(
        id=999,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    with pytest.raises(ValueError, match="Patient not found"):
        repository.update(patient)
