from datetime import UTC, date, datetime

from panda.database.schema_initializer import initialise_schema
from panda.models.appointment import Appointment, AppointmentStatus
from panda.models.patient import Patient
from panda.repositories.sqlite_appointment_repository import (
    SQLiteAppointmentRepository,
)
from panda.repositories.sqlite_patient_repository import (
    SQLitePatientRepository,
)


def test_booked_appointment_can_be_retrieved_from_database(tmp_path):
    database_path = tmp_path / "test_panda.db"

    # Initialise database schema
    initialise_schema(database_path)

    # Create and persist a patient first
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

    # Book an appointment for the saved patient
    appointment = Appointment(
        id=None,
        patient_id=saved_patient.id,
        start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
        status=AppointmentStatus.SCHEDULED,
    )

    saved_appointment = appointment_repository.save(appointment)

    # Retrieve appointment from database
    retrieved_appointment = appointment_repository.find_by_id(saved_appointment.id)

    # Verify retrieved appointment
    assert retrieved_appointment is not None
    assert retrieved_appointment.id == saved_appointment.id
    assert retrieved_appointment.patient_id == saved_patient.id
    assert retrieved_appointment.start_time == appointment.start_time
    assert retrieved_appointment.end_time == appointment.end_time
    assert retrieved_appointment.status == AppointmentStatus.SCHEDULED
