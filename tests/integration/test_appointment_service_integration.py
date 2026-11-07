from datetime import UTC, date, datetime

from panda.database.schema_initializer import initialise_schema
from panda.models.appointment import AppointmentStatus
from panda.models.patient import Patient
from panda.repositories.sqlite_appointment_repository import (
    SQLiteAppointmentRepository,
)
from panda.repositories.sqlite_patient_repository import (
    SQLitePatientRepository,
)
from panda.services.appointment_service import AppointmentService


def test_book_appointment_and_retrieve_from_database(tmp_path):
    database_path = tmp_path / "test_panda.db"

    # Initialise database
    initialise_schema(database_path)

    # Create and persist patient
    patient_repository = SQLitePatientRepository(database_path)

    patient = Patient(
        id=None,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 20),
        postcode="SW1A 1AA",
    )

    saved_patient = patient_repository.save(patient)

    # Create appointment repository
    appointment_repository = SQLiteAppointmentRepository(database_path)

    # Inject repositories into service
    appointment_service = AppointmentService(
        appointment_repository,
        patient_repository,
    )

    # Book appointment through service
    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 30, tzinfo=UTC)

    booked_appointment = appointment_service.book_appointment(
        patient_id=saved_patient.id,
        start_time=start_time,
        end_time=end_time,
    )

    # Retrieve appointment through service
    retrieved_appointment = appointment_service.get_appointment_by_id(
        booked_appointment.id
    )

    # Verify appointment
    assert retrieved_appointment is not None
    assert retrieved_appointment.id == booked_appointment.id
    assert retrieved_appointment.patient_id == saved_patient.id
    assert retrieved_appointment.start_time == start_time
    assert retrieved_appointment.end_time == end_time
    assert retrieved_appointment.status == AppointmentStatus.SCHEDULED
