from datetime import UTC, date, datetime
from unittest.mock import Mock

import pytest

from panda.database.schema_initializer import initialise_schema
from panda.models.appointment import Appointment, AppointmentStatus
from panda.repositories.appointment_repository_protocol import (
    AppointmentRepositoryProtocol,
)
from panda.repositories.patient_repository_protocol import (
    PatientRepositoryProtocol,
)
from panda.repositories.sqlite_appointment_repository import (
    SQLiteAppointmentRepository,
)
from panda.repositories.sqlite_patient_repository import (
    SQLitePatientRepository,
)
from panda.services.appointment_service import AppointmentService
from panda.services.patient_service import PatientService

# ---------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------


def create_mock_appointment_service(existing_appointments=None):
    appointment_repository = Mock(spec=AppointmentRepositoryProtocol)
    patient_repository = Mock(spec=PatientRepositoryProtocol)

    patient_repository.find_by_id.return_value = object()

    appointment_repository.find_by_patient_id.return_value = existing_appointments or []
    appointment_repository.save.side_effect = lambda appointment: appointment

    service = AppointmentService(
        appointment_repository=appointment_repository,
        patient_repository=patient_repository,
    )

    return service, appointment_repository, patient_repository


def create_existing_appointment(
    start_time,
    end_time,
    status=AppointmentStatus.SCHEDULED,
):
    return Appointment(
        id=1,
        patient_id=1,
        start_time=start_time,
        end_time=end_time,
        status=status,
    )


def create_test_patient(patient_repository):
    patient_service = PatientService(patient_repository)

    return patient_service.register_patient(
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )


# ---------------------------------------------------------------------
# Booking appointments
# ---------------------------------------------------------------------


def test_book_appointment_successfully():
    service, appointment_repository, patient_repository = (
        create_mock_appointment_service()
    )

    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 30, tzinfo=UTC)

    appointment = service.book_appointment(
        patient_id=1,
        start_time=start_time,
        end_time=end_time,
    )

    assert appointment is not None
    assert appointment.patient_id == 1
    assert appointment.start_time == start_time
    assert appointment.end_time == end_time
    assert appointment.status == AppointmentStatus.SCHEDULED

    patient_repository.find_by_id.assert_called_once_with(1)
    appointment_repository.find_by_patient_id.assert_called_once_with(1)
    appointment_repository.save.assert_called_once()


def test_book_appointment_rejects_non_existing_patient():
    service, appointment_repository, patient_repository = (
        create_mock_appointment_service()
    )

    patient_repository.find_by_id.return_value = None

    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 30, tzinfo=UTC)

    with pytest.raises(ValueError, match="Patient not found"):
        service.book_appointment(
            patient_id=999,
            start_time=start_time,
            end_time=end_time,
        )

    patient_repository.find_by_id.assert_called_once_with(999)
    appointment_repository.save.assert_not_called()


def test_book_appointment_rejects_start_time_after_end_time():
    service, appointment_repository, _ = create_mock_appointment_service()

    start_time = datetime(2026, 11, 10, 11, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="Appointment start time must be before end time",
    ):
        service.book_appointment(
            patient_id=1,
            start_time=start_time,
            end_time=end_time,
        )

    appointment_repository.save.assert_not_called()


def test_book_appointment_rejects_timezone_naive_start_time():
    service, appointment_repository, _ = create_mock_appointment_service()

    start_time = datetime(2026, 11, 10, 10, 0)
    end_time = datetime(2026, 11, 10, 10, 30, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="Appointment start time must be timezone-aware",
    ):
        service.book_appointment(
            patient_id=1,
            start_time=start_time,
            end_time=end_time,
        )

    appointment_repository.save.assert_not_called()


def test_book_appointment_rejects_timezone_naive_end_time():
    service, appointment_repository, _ = create_mock_appointment_service()

    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 30)

    with pytest.raises(
        ValueError,
        match="Appointment end time must be timezone-aware",
    ):
        service.book_appointment(
            patient_id=1,
            start_time=start_time,
            end_time=end_time,
        )

    appointment_repository.save.assert_not_called()


# ---------------------------------------------------------------------
# Appointment overlap validation
# ---------------------------------------------------------------------


def test_book_appointment_rejects_overlapping_appointment():
    existing_appointment = create_existing_appointment(
        datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
    )

    service, appointment_repository, _ = create_mock_appointment_service(
        [existing_appointment]
    )

    with pytest.raises(
        ValueError,
        match="already has an appointment",
    ):
        service.book_appointment(
            patient_id=1,
            start_time=datetime(2026, 11, 10, 10, 15, tzinfo=UTC),
            end_time=datetime(2026, 11, 10, 10, 45, tzinfo=UTC),
        )

    appointment_repository.save.assert_not_called()


def test_book_appointment_rejects_overlap_when_new_appointment_starts_earlier():
    existing_appointment = create_existing_appointment(
        datetime(2026, 11, 10, 10, 15, tzinfo=UTC),
        datetime(2026, 11, 10, 10, 45, tzinfo=UTC),
    )

    service, appointment_repository, _ = create_mock_appointment_service(
        [existing_appointment]
    )

    with pytest.raises(
        ValueError,
        match="already has an appointment",
    ):
        service.book_appointment(
            patient_id=1,
            start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
        )

    appointment_repository.save.assert_not_called()


def test_book_appointment_rejects_new_appointment_inside_existing_appointment():
    existing_appointment = create_existing_appointment(
        datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        datetime(2026, 11, 10, 11, 0, tzinfo=UTC),
    )

    service, appointment_repository, _ = create_mock_appointment_service(
        [existing_appointment]
    )

    with pytest.raises(
        ValueError,
        match="already has an appointment",
    ):
        service.book_appointment(
            patient_id=1,
            start_time=datetime(2026, 11, 10, 10, 15, tzinfo=UTC),
            end_time=datetime(2026, 11, 10, 10, 45, tzinfo=UTC),
        )

    appointment_repository.save.assert_not_called()


def test_book_appointment_allows_back_to_back_appointments():
    existing_appointment = create_existing_appointment(
        datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
    )

    service, appointment_repository, _ = create_mock_appointment_service(
        [existing_appointment]
    )

    appointment = service.book_appointment(
        patient_id=1,
        start_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 11, 0, tzinfo=UTC),
    )

    assert appointment is not None
    assert appointment.patient_id == 1
    appointment_repository.save.assert_called_once()


@pytest.mark.parametrize(
    "status",
    [
        AppointmentStatus.CANCELLED,
        AppointmentStatus.ATTENDED,
        AppointmentStatus.MISSED,
    ],
)
def test_book_appointment_allows_booking_when_existing_appointment_is_not_scheduled(
    status,
):
    existing_appointment = create_existing_appointment(
        datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
        status=status,
    )

    service, appointment_repository, _ = create_mock_appointment_service(
        [existing_appointment]
    )

    appointment = service.book_appointment(
        patient_id=1,
        start_time=datetime(2026, 11, 10, 10, 15, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 10, 45, tzinfo=UTC),
    )

    assert appointment is not None
    assert appointment.patient_id == 1
    appointment_repository.save.assert_called_once()


# ---------------------------------------------------------------------
# SQLite appointment booking
# ---------------------------------------------------------------------


@pytest.fixture
def sqlite_appointment_service(tmp_path):
    database_path = tmp_path / "test_panda.db"

    initialise_schema(database_path=database_path)

    patient_repository = SQLitePatientRepository(database_path=database_path)

    appointment_repository = SQLiteAppointmentRepository(database_path=database_path)

    service = AppointmentService(
        appointment_repository=appointment_repository,
        patient_repository=patient_repository,
    )

    return service, patient_repository


def test_book_appointment_with_sqlite(sqlite_appointment_service):
    appointment_service, patient_repository = sqlite_appointment_service

    patient = create_test_patient(patient_repository)

    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 30, tzinfo=UTC)

    appointment = appointment_service.book_appointment(
        patient_id=patient.id,
        start_time=start_time,
        end_time=end_time,
    )

    assert appointment.id is not None
    assert appointment.patient_id == patient.id
    assert appointment.start_time == start_time
    assert appointment.end_time == end_time
    assert appointment.status == AppointmentStatus.SCHEDULED


# ---------------------------------------------------------------------
# Retrieving appointments
# ---------------------------------------------------------------------


def test_get_appointment_by_id_successfully():
    service, appointment_repository, _ = create_mock_appointment_service()

    expected_appointment = Appointment(
        id=1,
        patient_id=10,
        start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
    )

    appointment_repository.find_by_id.return_value = expected_appointment

    result = service.get_appointment_by_id(1)

    assert result == expected_appointment
    appointment_repository.find_by_id.assert_called_once_with(1)


def test_get_appointment_by_id_returns_none_when_not_found():
    service, appointment_repository, _ = create_mock_appointment_service()

    appointment_repository.find_by_id.return_value = None

    result = service.get_appointment_by_id(999)

    assert result is None
    appointment_repository.find_by_id.assert_called_once_with(999)


# ---------------------------------------------------------------------
# Updating appointment status
# ---------------------------------------------------------------------


def test_update_appointment_status_successfully():
    service, appointment_repository, _ = create_mock_appointment_service()

    appointment = Appointment(
        id=1,
        patient_id=1,
        start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
    )

    appointment_repository.find_by_id.return_value = appointment
    appointment_repository.update.side_effect = lambda item: item

    result = service.update_appointment_status(
        appointment_id=1,
        status=AppointmentStatus.ATTENDED,
    )

    assert result is not None
    assert result.status == AppointmentStatus.ATTENDED

    appointment_repository.find_by_id.assert_called_once_with(1)
    appointment_repository.update.assert_called_once_with(appointment)


def test_update_appointment_status_returns_none_when_not_found():
    service, appointment_repository, _ = create_mock_appointment_service()

    appointment_repository.find_by_id.return_value = None

    result = service.update_appointment_status(
        appointment_id=999,
        status=AppointmentStatus.ATTENDED,
    )

    assert result is None
    appointment_repository.update.assert_not_called()


# ---------------------------------------------------------------------
# Cancelling appointments
# ---------------------------------------------------------------------


def test_cancel_appointment_successfully():
    service, appointment_repository, _ = create_mock_appointment_service()

    appointment = Appointment(
        id=1,
        patient_id=1,
        start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
    )

    appointment_repository.find_by_id.return_value = appointment
    appointment_repository.update.side_effect = lambda item: item

    result = service.cancel_appointment(1)

    assert result is not None
    assert result.status == AppointmentStatus.CANCELLED

    appointment_repository.find_by_id.assert_called_once_with(1)
    appointment_repository.update.assert_called_once_with(appointment)


def test_cancel_appointment_returns_none_when_not_found():
    service, appointment_repository, _ = create_mock_appointment_service()

    appointment_repository.find_by_id.return_value = None

    result = service.cancel_appointment(999)

    assert result is None
    appointment_repository.update.assert_not_called()


# ---------------------------------------------------------------------
# SQLite appointment status and cancellation integration
# ---------------------------------------------------------------------


def test_update_appointment_status_with_sqlite(sqlite_appointment_service):
    appointment_service, patient_repository = sqlite_appointment_service

    patient = create_test_patient(patient_repository)

    appointment = appointment_service.book_appointment(
        patient_id=patient.id,
        start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
    )

    updated_appointment = appointment_service.update_appointment_status(
        appointment_id=appointment.id,
        status=AppointmentStatus.ATTENDED,
    )

    assert updated_appointment is not None
    assert updated_appointment.id == appointment.id
    assert updated_appointment.status == AppointmentStatus.ATTENDED

    retrieved_appointment = appointment_service.get_appointment_by_id(appointment.id)

    assert retrieved_appointment.status == AppointmentStatus.ATTENDED


def test_cancel_appointment_with_sqlite(sqlite_appointment_service):
    appointment_service, patient_repository = sqlite_appointment_service

    patient = create_test_patient(patient_repository)

    appointment = appointment_service.book_appointment(
        patient_id=patient.id,
        start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
    )

    cancelled_appointment = appointment_service.cancel_appointment(appointment.id)

    assert cancelled_appointment is not None
    assert cancelled_appointment.status == AppointmentStatus.CANCELLED

    retrieved_appointment = appointment_service.get_appointment_by_id(appointment.id)

    assert retrieved_appointment.status == AppointmentStatus.CANCELLED
