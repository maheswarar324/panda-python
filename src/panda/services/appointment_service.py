from datetime import datetime

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


class AppointmentService:
    def __init__(
        self,
        appointment_repository: AppointmentRepositoryProtocol | None = None,
        patient_repository: PatientRepositoryProtocol | None = None,
    ) -> None:
        self._appointment_repository = (
            appointment_repository or SQLiteAppointmentRepository()
        )
        self._patient_repository = patient_repository or SQLitePatientRepository()

    def book_appointment(
        self,
        patient_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Appointment:
        # Validate patient existence
        patient = self._patient_repository.find_by_id(patient_id)

        if patient is None:
            raise ValueError("Patient not found")

        # Create the appointment first to trigger model validation
        appointment = Appointment(
            patient_id=patient_id,
            start_time=start_time,
            end_time=end_time,
            status=AppointmentStatus.SCHEDULED,
        )

        # Check for overlapping scheduled appointments
        existing_appointments = self._appointment_repository.find_by_patient_id(
            patient_id
        )

        for existing_appointment in existing_appointments:
            if existing_appointment.status != AppointmentStatus.SCHEDULED:
                continue

            if (
                start_time < existing_appointment.end_time
                and end_time > existing_appointment.start_time
            ):
                raise ValueError("Patient already has an appointment during this time")

        # Save only after all existing appointments have been checked
        return self._appointment_repository.save(appointment)

    def get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
        return self._appointment_repository.find_by_id(appointment_id)

    def update_appointment_status(
        self,
        appointment_id: int,
        status: AppointmentStatus,
    ) -> Appointment | None:
        appointment = self._appointment_repository.find_by_id(appointment_id)

        if appointment is None:
            return None

        appointment.status = status

        return self._appointment_repository.update(appointment)

    def cancel_appointment(
        self,
        appointment_id: int,
    ) -> Appointment | None:
        return self.update_appointment_status(
            appointment_id,
            AppointmentStatus.CANCELLED,
        )
