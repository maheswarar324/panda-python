from datetime import datetime

from panda.exceptions.invalid_appointment_state_error import (
    InvalidAppointmentStateError,
)
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
            appointment_repository
            if appointment_repository is not None
            else SQLiteAppointmentRepository()
        )
        self._patient_repository = (
            patient_repository
            if patient_repository is not None
            else SQLitePatientRepository()
        )

    def book_appointment(
        self,
        patient_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Appointment:
        """Book an appointment for an existing patient."""

        patient = self._patient_repository.find_by_id(patient_id)

        if patient is None:
            raise ValueError("Patient not found")

        # Create the appointment first to trigger model validation.
        appointment = Appointment(
            patient_id=patient_id,
            start_time=start_time,
            end_time=end_time,
            status=AppointmentStatus.SCHEDULED,
        )

        # Check for overlapping scheduled appointments.
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

        return self._appointment_repository.save(appointment)

    def get_appointment_by_id(
        self,
        appointment_id: int,
    ) -> Appointment | None:
        """Retrieve an appointment by ID."""

        return self._appointment_repository.find_by_id(appointment_id)

    def update_appointment_status(
        self,
        appointment_id: int,
        status: AppointmentStatus,
    ) -> Appointment | None:
        """Update the status of a scheduled appointment."""

        if not isinstance(status, AppointmentStatus):
            raise TypeError("Invalid appointment status")

        appointment = self._appointment_repository.find_by_id(appointment_id)

        if appointment is None:
            return None

        if appointment.status != AppointmentStatus.SCHEDULED:
            raise InvalidAppointmentStateError(
                f"Cannot change appointment status from "
                f"{appointment.status.value} to {status.value}"
            )

        appointment.status = status

        return self._appointment_repository.update(appointment)

    def reschedule_appointment(
        self,
        appointment_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Appointment | None:
        """Reschedule an existing scheduled appointment."""

        appointment = self._appointment_repository.find_by_id(appointment_id)

        if appointment is None:
            return None

        # Only scheduled appointments can be rescheduled.
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise InvalidAppointmentStateError(
                f"Cannot reschedule appointment with status {appointment.status.value}"
            )

        # Create a candidate appointment to trigger model validation.
        candidate = Appointment(
            id=appointment.id,
            patient_id=appointment.patient_id,
            start_time=start_time,
            end_time=end_time,
            status=appointment.status,
        )

        # Check for overlapping scheduled appointments.
        existing_appointments = self._appointment_repository.find_by_patient_id(
            appointment.patient_id
        )

        for existing_appointment in existing_appointments:
            # Exclude the appointment being rescheduled.
            if existing_appointment.id == appointment_id:
                continue

            if existing_appointment.status != AppointmentStatus.SCHEDULED:
                continue

            if (
                candidate.start_time < existing_appointment.end_time
                and candidate.end_time > existing_appointment.start_time
            ):
                raise ValueError("Patient already has an appointment during this time")

        # Apply changes only after all validations pass.
        appointment.start_time = candidate.start_time
        appointment.end_time = candidate.end_time

        return self._appointment_repository.update(appointment)

    def cancel_appointment(
        self,
        appointment_id: int,
    ) -> Appointment | None:
        """Cancel an existing scheduled appointment."""

        return self.update_appointment_status(
            appointment_id,
            AppointmentStatus.CANCELLED,
        )
