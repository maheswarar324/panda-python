from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from panda.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    patient_id: int
    start_time: datetime
    end_time: datetime

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")

        return value


class AppointmentReschedule(BaseModel):
    start_time: datetime
    end_time: datetime

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information")

        return value


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
