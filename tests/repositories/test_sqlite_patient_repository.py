import sqlite3
from datetime import date

import pytest

from panda.database.schema_initializer import initialise_schema
from panda.models.patient import Patient
from panda.repositories.sqlite_patient_repository import SQLitePatientRepository


@pytest.fixture
def patient_repository(tmp_path):
    database_path = tmp_path / "test_panda.db"

    initialise_schema(database_path)

    return SQLitePatientRepository(database_path=database_path)


@pytest.fixture
def patient():
    return Patient(
        id=None,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )


def test_save_patient(patient_repository, patient):
    saved_patient = patient_repository.save(patient)

    assert saved_patient.id == 1


def test_save_patient_rejects_duplicate_nhs_number(patient_repository, patient):
    patient_repository.save(patient)

    duplicate_patient = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1992, 3, 15),
        postcode="SW1A 2AA",
    )

    with pytest.raises(sqlite3.IntegrityError):
        patient_repository.save(duplicate_patient)


def test_save_patient_persists_data(patient_repository, patient):
    saved_patient = patient_repository.save(patient)

    retrieved_patient = patient_repository.find_by_id(saved_patient.id)

    assert retrieved_patient is not None
    assert retrieved_patient.nhs_number == patient.nhs_number
    assert retrieved_patient.first_name == patient.first_name
    assert retrieved_patient.last_name == patient.last_name
    assert retrieved_patient.date_of_birth == patient.date_of_birth
    assert retrieved_patient.postcode == patient.postcode


def test_save_patient_assigns_sequential_ids(patient_repository, patient):
    first_patient = patient_repository.save(patient)

    second_patient = Patient(
        id=None,
        nhs_number="9434765927",
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1992, 8, 15),
        postcode="M1 1AA",
    )

    second_patient = patient_repository.save(second_patient)

    assert first_patient.id == 1
    assert second_patient.id == 2


def test_find_by_id_returns_patient(patient_repository, patient):
    saved_patient = patient_repository.save(patient)

    retrieved_patient = patient_repository.find_by_id(saved_patient.id)

    assert retrieved_patient is not None
    assert retrieved_patient.id == saved_patient.id
    assert retrieved_patient.nhs_number == saved_patient.nhs_number
    assert retrieved_patient.first_name == saved_patient.first_name


def test_find_by_id_returns_none_when_not_found(patient_repository):
    assert patient_repository.find_by_id(999) is None


def test_find_by_nhs_number_returns_patient(patient_repository, patient):
    saved_patient = patient_repository.save(patient)

    retrieved_patient = patient_repository.find_by_nhs_number(saved_patient.nhs_number)

    assert retrieved_patient is not None
    assert retrieved_patient.id == saved_patient.id
    assert retrieved_patient.nhs_number == saved_patient.nhs_number


def test_find_by_nhs_number_returns_none_when_not_found(
    patient_repository,
):
    assert patient_repository.find_by_nhs_number("9434765919") is None


def test_update_patient(patient_repository, patient):
    saved_patient = patient_repository.save(patient)

    saved_patient.postcode = "SW1A 2AA"

    updated_patient = patient_repository.update(saved_patient)

    assert updated_patient is not None
    assert updated_patient.id == saved_patient.id
    assert updated_patient.postcode == "SW1A 2AA"


def test_update_patient_persists_all_changes(patient_repository, patient):
    saved_patient = patient_repository.save(patient)

    saved_patient.first_name = "Jonathan"
    saved_patient.last_name = "Brown"
    saved_patient.date_of_birth = date(1988, 10, 12)
    saved_patient.postcode = "M1 1AA"

    patient_repository.update(saved_patient)

    retrieved_patient = patient_repository.find_by_id(saved_patient.id)

    assert retrieved_patient is not None
    assert retrieved_patient.first_name == "Jonathan"
    assert retrieved_patient.last_name == "Brown"
    assert retrieved_patient.date_of_birth == date(1988, 10, 12)
    assert retrieved_patient.postcode == "M1 1AA"


def test_update_patient_returns_none_when_not_found(patient_repository, patient):
    patient.id = 999

    updated_patient = patient_repository.update(patient)

    assert updated_patient is None


def test_update_patient_does_not_insert_when_not_found(patient_repository, patient):
    patient.id = 999

    patient_repository.update(patient)

    assert patient_repository.find_all() == []


def test_update_patient_rejects_duplicate_nhs_number(patient_repository, patient):
    patient_repository.save(patient)

    second_patient = Patient(
        id=None,
        nhs_number="9434765927",
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1992, 8, 15),
        postcode="M1 1AA",
    )

    saved_second_patient = patient_repository.save(second_patient)
    saved_second_patient.nhs_number = "9434765919"

    with pytest.raises(sqlite3.IntegrityError):
        patient_repository.update(saved_second_patient)


def test_find_all_returns_all_patients(patient_repository, patient):
    patient_repository.save(patient)

    second_patient = Patient(
        id=None,
        nhs_number="9434765927",
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1992, 8, 15),
        postcode="M1 1AA",
    )

    patient_repository.save(second_patient)

    patients = patient_repository.find_all()

    assert len(patients) == 2
    assert patients[0].first_name == "John"
    assert patients[1].first_name == "Jane"


def test_find_all_returns_empty_list_when_no_patients(
    patient_repository,
):
    assert patient_repository.find_all() == []


def test_delete_patient(patient_repository, patient):
    saved_patient = patient_repository.save(patient)

    result = patient_repository.delete_by_id(saved_patient.id)

    assert result is True
    assert patient_repository.find_by_id(saved_patient.id) is None


def test_delete_patient_returns_false_when_not_found(
    patient_repository,
):
    assert patient_repository.delete_by_id(999) is False


def test_database_persistence_across_repository_instances(tmp_path, patient):
    database_path = tmp_path / "test_panda.db"

    initialise_schema(database_path)

    first_repository = SQLitePatientRepository(database_path=database_path)

    saved_patient = first_repository.save(patient)

    second_repository = SQLitePatientRepository(database_path=database_path)

    retrieved_patient = second_repository.find_by_id(saved_patient.id)

    assert retrieved_patient is not None
    assert retrieved_patient.id == saved_patient.id
    assert retrieved_patient.nhs_number == saved_patient.nhs_number
    assert retrieved_patient.first_name == saved_patient.first_name
