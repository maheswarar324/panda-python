from datetime import UTC, datetime

import pytest

from panda.models.appointment import Appointment, AppointmentStatus


def test_appointment_creation():
    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 30, tzinfo=UTC)

    appointment = Appointment(
        patient_id=1,
        start_time=start_time,
        end_time=end_time,
    )

    assert appointment.id is None
    assert appointment.patient_id == 1
    assert appointment.start_time == start_time
    assert appointment.end_time == end_time
    assert appointment.status == AppointmentStatus.SCHEDULED


def test_appointment_with_explicit_status():
    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)
    end_time = datetime(2026, 11, 10, 10, 30, tzinfo=UTC)

    appointment = Appointment(
        patient_id=1,
        start_time=start_time,
        end_time=end_time,
        status=AppointmentStatus.ATTENDED,
    )

    assert appointment.status == AppointmentStatus.ATTENDED


def test_appointment_rejects_invalid_patient_id():
    with pytest.raises(ValueError, match="Patient ID must be positive"):
        Appointment(
            patient_id=0,
            start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
        )


def test_appointment_rejects_naive_start_time():
    with pytest.raises(ValueError, match="start time must be timezone-aware"):
        Appointment(
            patient_id=1,
            start_time=datetime(2026, 11, 10, 10, 0),
            end_time=datetime(2026, 11, 10, 10, 30, tzinfo=UTC),
        )


def test_appointment_rejects_naive_end_time():
    with pytest.raises(ValueError, match="end time must be timezone-aware"):
        Appointment(
            patient_id=1,
            start_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 11, 10, 10, 30),
        )


def test_appointment_rejects_start_time_after_end_time():
    with pytest.raises(ValueError, match="start time must be before end time"):
        Appointment(
            patient_id=1,
            start_time=datetime(2026, 11, 10, 11, 0, tzinfo=UTC),
            end_time=datetime(2026, 11, 10, 10, 0, tzinfo=UTC),
        )


def test_appointment_rejects_equal_start_and_end_times():
    start_time = datetime(2026, 11, 10, 10, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="start time must be before end time"):
        Appointment(
            patient_id=1,
            start_time=start_time,
            end_time=start_time,
        )
