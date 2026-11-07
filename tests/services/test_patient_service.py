from datetime import date

import pytest

from panda.database.schema_initializer import initialise_schema
from panda.repositories.fake_patient_repository import FakePatientRepository
from panda.repositories.patient_repository import PatientRepository
from panda.repositories.sqlite_patient_repository import SQLitePatientRepository
from panda.services.patient_service import PatientService


@pytest.fixture
def sqlite_patient_service(tmp_path):
    database_path = tmp_path / "test_panda.db"
    initialise_schema(database_path=database_path)
    repository = SQLitePatientRepository(database_path=database_path)

    return PatientService(repository)


def test_register_patient():
    patient_service = PatientService(PatientRepository())

    patient = patient_service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    assert patient.id == 1
    assert patient.first_name == "John"
    assert patient.last_name == "Smith"
    assert patient.nhs_number == "9434765919"
    assert patient.date_of_birth == date(1990, 5, 20)
    assert patient.postcode == "SW1A 1AA"


def test_register_patient_rejects_invalid_nhs_number():
    patient_service = PatientService(PatientRepository())

    with pytest.raises(ValueError, match="Invalid NHS number"):
        patient_service.register_patient(
            nhs_number="123",
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 5, 20),
            postcode="SW1A 1AA",
        )


def test_register_patient_rejects_duplicate_nhs_number():
    service = PatientService(PatientRepository())

    service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    with pytest.raises(ValueError, match="already exists"):
        service.register_patient(
            nhs_number="9434765919",
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(1992, 3, 15),
            postcode="SW1A 1AA",
        )


def test_update_patient_postcode():
    service = PatientService()

    patient = service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    updated_patient = service.update_patient_postcode(
        patient_id=patient.id,
        postcode="SW1A 2AA",
    )

    assert updated_patient.id == patient.id
    assert updated_patient.postcode == "SW1A 2AA"
    assert updated_patient.nhs_number == patient.nhs_number


def test_update_patient_postcode_rejects_invalid_postcode():
    service = PatientService()

    patient = service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    with pytest.raises(ValueError, match="Invalid UK postcode"):
        service.update_patient_postcode(
            patient_id=patient.id,
            postcode="INVALID",
        )


def test_update_patient_postcode_raises_error_when_patient_not_found():
    service = PatientService()

    with pytest.raises(ValueError, match="Patient not found"):
        service.update_patient_postcode(
            patient_id=999,
            postcode="SW1A 2AA",
        )


def test_get_patient_by_id():
    service = PatientService()

    registered_patient = service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    patient = service.get_patient_by_id(registered_patient.id)

    assert patient is not None
    assert patient.id == registered_patient.id
    assert patient.first_name == "John"
    assert patient.nhs_number == "9434765919"


def test_get_patient_by_id_returns_none_when_not_found():
    service = PatientService()

    patient = service.get_patient_by_id(999)

    assert patient is None


def test_patient_service_accepts_different_repository_implementation():
    repository = FakePatientRepository()
    service = PatientService(repository)

    patient = service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    assert patient.id == 1
    assert repository.find_by_id(1) is patient


def test_patient_service_with_sqlite_repository(sqlite_patient_service):
    patient = sqlite_patient_service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    retrieved_patient = sqlite_patient_service.get_patient_by_id(patient.id)

    assert retrieved_patient is not None
    assert retrieved_patient.id == patient.id
    assert retrieved_patient.first_name == "John"
    assert retrieved_patient.nhs_number == "9434765919"


def test_patient_service_with_sqlite_rejects_duplicate_nhs_number(
    sqlite_patient_service,
):
    sqlite_patient_service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    with pytest.raises(ValueError, match="already exists"):
        sqlite_patient_service.register_patient(
            nhs_number="9434765919",
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(1992, 3, 15),
            postcode="SW1A 2AA",
        )


def test_patient_service_with_sqlite_updates_patient_postcode(
    sqlite_patient_service,
):
    patient = sqlite_patient_service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    updated_patient = sqlite_patient_service.update_patient_postcode(
        patient_id=patient.id,
        postcode="SW1A 2AA",
    )

    assert updated_patient.id == patient.id
    assert updated_patient.postcode == "SW1A 2AA"

    retrieved_patient = sqlite_patient_service.get_patient_by_id(patient.id)

    assert retrieved_patient is not None
    assert retrieved_patient.postcode == "SW1A 2AA"


def test_delete_patient():
    service = PatientService()

    patient = service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    result = service.delete_patient(patient.id)

    assert result is True
    assert service.get_patient_by_id(patient.id) is None


def test_delete_patient_returns_false_when_patient_not_found():
    service = PatientService()
    result = service.delete_patient(patient_id=999)

    assert result is False


def test_patient_service_with_sqlite_deletes_patient(
    sqlite_patient_service,
):
    patient = sqlite_patient_service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    result = sqlite_patient_service.delete_patient(patient_id=patient.id)
    assert result is True

    retrieved_patient = sqlite_patient_service.get_patient_by_id(patient.id)
    assert retrieved_patient is None


def test_get_patient_by_nhs_number():
    service = PatientService()

    registered_patient = service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    patient = service.get_patient_by_nhs_number("9434765919")

    assert patient is not None
    assert patient.id == registered_patient.id
    assert patient.first_name == "John"
