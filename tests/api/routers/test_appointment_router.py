from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from panda.api.dependencies.appointment_dependencies import (
    get_appointment_service,
)
from panda.api.routers.appointment_router import router
from panda.models.appointment import Appointment, AppointmentStatus
from panda.services.appointment_service import AppointmentService


@pytest.fixture
def appointment_service():
    return MagicMock(spec=AppointmentService)


@pytest.fixture
def client(appointment_service):
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[get_appointment_service] = lambda: appointment_service

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def sample_appointment():
    return Appointment(
        id=10,
        patient_id=1,
        start_time=datetime(2026, 11, 15, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 15, 10, 30, tzinfo=UTC),
        status=AppointmentStatus.SCHEDULED,
    )


@pytest.fixture
def appointment_payload():
    return {
        "patient_id": 1,
        "start_time": "2026-11-15T10:00:00+00:00",
        "end_time": "2026-11-15T10:30:00+00:00",
    }


@pytest.fixture
def reschedule_payload():
    return {
        "start_time": "2026-11-15T11:00:00+00:00",
        "end_time": "2026-11-15T11:30:00+00:00",
    }


# ---------------------------------------------------------
# POST /appointments
# ---------------------------------------------------------


def test_create_appointment_success(
    client,
    appointment_service,
    sample_appointment,
    appointment_payload,
):
    appointment_service.book_appointment.return_value = sample_appointment

    response = client.post(
        "/appointments",
        json=appointment_payload,
    )

    assert response.status_code == 201
    assert response.json()["id"] == 10
    assert response.json()["patient_id"] == 1
    assert response.json()["status"] == "SCHEDULED"

    appointment_service.book_appointment.assert_called_once_with(
        1,
        sample_appointment.start_time,
        sample_appointment.end_time,
    )


def test_create_appointment_patient_not_found(
    client,
    appointment_service,
    appointment_payload,
):
    appointment_service.book_appointment.side_effect = ValueError("Patient not found")

    response = client.post(
        "/appointments",
        json=appointment_payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_create_appointment_overlap_conflict(
    client,
    appointment_service,
    appointment_payload,
):
    appointment_service.book_appointment.side_effect = ValueError(
        "Patient already has an appointment during this time"
    )

    response = client.post(
        "/appointments",
        json=appointment_payload,
    )

    assert response.status_code == 409
    assert "already has an appointment" in response.json()["detail"]


def test_create_appointment_invalid_time_range(
    client,
    appointment_service,
    appointment_payload,
):
    appointment_service.book_appointment.side_effect = ValueError(
        "Appointment start time must be before end time"
    )

    response = client.post(
        "/appointments",
        json=appointment_payload,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Appointment start time must be before end time"
    )


def test_create_appointment_rejects_missing_timezone(
    client,
    appointment_service,
):
    payload = {
        "patient_id": 1,
        "start_time": "2026-11-15T10:00:00",
        "end_time": "2026-11-15T10:30:00",
    }

    response = client.post(
        "/appointments",
        json=payload,
    )

    assert response.status_code == 422
    appointment_service.book_appointment.assert_not_called()


# ---------------------------------------------------------
# GET /appointments/{appointment_id}
# ---------------------------------------------------------


def test_get_appointment_success(
    client,
    appointment_service,
    sample_appointment,
):
    appointment_service.get_appointment_by_id.return_value = sample_appointment

    response = client.get("/appointments/10")

    assert response.status_code == 200
    assert response.json()["id"] == 10
    assert response.json()["patient_id"] == 1
    assert response.json()["status"] == "SCHEDULED"

    appointment_service.get_appointment_by_id.assert_called_once_with(10)


def test_get_appointment_not_found(
    client,
    appointment_service,
):
    appointment_service.get_appointment_by_id.return_value = None

    response = client.get("/appointments/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"


# ---------------------------------------------------------
# PATCH /appointments/{appointment_id}/status
# ---------------------------------------------------------


def test_update_appointment_status_success(
    client,
    appointment_service,
    sample_appointment,
):
    sample_appointment.status = AppointmentStatus.ATTENDED

    appointment_service.update_appointment_status.return_value = sample_appointment

    response = client.patch(
        "/appointments/10/status",
        json={"status": "ATTENDED"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ATTENDED"

    appointment_service.update_appointment_status.assert_called_once_with(
        10,
        AppointmentStatus.ATTENDED,
    )


def test_update_appointment_status_not_found(
    client,
    appointment_service,
):
    appointment_service.update_appointment_status.return_value = None

    response = client.patch(
        "/appointments/999/status",
        json={"status": "ATTENDED"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"


def test_update_appointment_status_invalid_status(
    client,
    appointment_service,
):
    response = client.patch(
        "/appointments/10/status",
        json={"status": "INVALID"},
    )

    assert response.status_code == 422
    appointment_service.update_appointment_status.assert_not_called()


# ---------------------------------------------------------
# PATCH /appointments/{appointment_id}/cancel
# ---------------------------------------------------------


def test_cancel_appointment_success(
    client,
    appointment_service,
    sample_appointment,
):
    sample_appointment.status = AppointmentStatus.CANCELLED

    appointment_service.cancel_appointment.return_value = sample_appointment

    response = client.patch("/appointments/10/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"

    appointment_service.cancel_appointment.assert_called_once_with(10)


def test_cancel_appointment_not_found(
    client,
    appointment_service,
):
    appointment_service.cancel_appointment.return_value = None

    response = client.patch("/appointments/999/cancel")

    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"


# ---------------------------------------------------------
# PATCH /appointments/{appointment_id}/reschedule
# ---------------------------------------------------------


def test_reschedule_appointment_success(
    client,
    appointment_service,
    sample_appointment,
    reschedule_payload,
):
    new_start_time = datetime(2026, 11, 15, 11, 0, tzinfo=UTC)
    new_end_time = datetime(2026, 11, 15, 11, 30, tzinfo=UTC)

    sample_appointment.start_time = new_start_time
    sample_appointment.end_time = new_end_time

    appointment_service.reschedule_appointment.return_value = sample_appointment

    response = client.patch(
        "/appointments/10/reschedule",
        json=reschedule_payload,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == 10
    assert response_data["patient_id"] == 1
    assert response_data["start_time"] == "2026-11-15T11:00:00Z"
    assert response_data["end_time"] == "2026-11-15T11:30:00Z"
    assert response_data["status"] == "SCHEDULED"

    appointment_service.reschedule_appointment.assert_called_once_with(
        10,
        new_start_time,
        new_end_time,
    )


def test_reschedule_appointment_not_found(
    client,
    appointment_service,
    reschedule_payload,
):
    appointment_service.reschedule_appointment.return_value = None

    response = client.patch(
        "/appointments/999/reschedule",
        json=reschedule_payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"

    appointment_service.reschedule_appointment.assert_called_once_with(
        999,
        datetime(2026, 11, 15, 11, 0, tzinfo=UTC),
        datetime(2026, 11, 15, 11, 30, tzinfo=UTC),
    )
