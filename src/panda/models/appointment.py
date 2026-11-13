from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    ATTENDED = "ATTENDED"
    CANCELLED = "CANCELLED"
    MISSED = "MISSED"


@dataclass
class Appointment:
    patient_id: int
    start_time: datetime
    end_time: datetime
    id: int | None = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED

    def __post_init__(self) -> None:
        if self.patient_id <= 0:
            raise ValueError("Patient ID must be positive")

        if not isinstance(self.status, AppointmentStatus):
            raise TypeError("Invalid appointment status")

        if self.start_time.tzinfo is None or self.start_time.utcoffset() is None:
            raise ValueError("Appointment start time must be timezone-aware")

        if self.end_time.tzinfo is None or self.end_time.utcoffset() is None:
            raise ValueError("Appointment end time must be timezone-aware")

        if self.start_time >= self.end_time:
            raise ValueError("Appointment start time must be before end time")
