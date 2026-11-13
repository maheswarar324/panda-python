from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from panda.api.schemas.appointment_schemas import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
)
from panda.models.appointment import Appointment, AppointmentStatus


def test_create_appointment():
    data = AppointmentCreate(
        patient_id=1,
        start_time=datetime(2026, 11, 15, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 15, 10, 30, tzinfo=UTC),
    )

    assert data.patient_id == 1
    assert data.start_time.hour == 10
    assert data.end_time.hour == 10


def test_update_appointment_status():
    data = AppointmentStatusUpdate(status="CANCELLED")

    assert data.status == AppointmentStatus.CANCELLED


def test_update_appointment_status_rejects_invalid_status():
    with pytest.raises(ValidationError):
        AppointmentStatusUpdate(status="INVALID")


def test_appointment_response_from_domain_model():
    appointment = Appointment(
        id=1,
        patient_id=10,
        start_time=datetime(2026, 11, 15, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 15, 10, 30, tzinfo=UTC),
    )

    response = AppointmentResponse.model_validate(appointment)

    assert response.id == 1
    assert response.patient_id == 10
    assert response.status == AppointmentStatus.SCHEDULED
