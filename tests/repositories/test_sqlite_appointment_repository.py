import sqlite3
from datetime import UTC, datetime

import pytest

from panda.models.appointment import Appointment, AppointmentStatus
from panda.repositories.sqlite_appointment_repository import (
    SQLiteAppointmentRepository,
)


@pytest.fixture
def appointment_repository(tmp_path):
    database_path = tmp_path / "test_panda.db"
    connection = sqlite3.connect(database_path)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("""
            CREATE TABLE patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nhs_number TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                postcode TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)

        connection.execute(
            """
            INSERT INTO patients (
                nhs_number,
                first_name,
                last_name,
                date_of_birth,
                postcode
            )
            VALUES (?, ?, ?, ?, ?)
        """,
            ("9434765919", "John", "Smith", "1990-05-20", "SW1A 1AA"),
        )

        connection.commit()
    finally:
        connection.close()

    return SQLiteAppointmentRepository(database_path=database_path)


@pytest.fixture
def appointment():
    return Appointment(
        id=None,
        patient_id=1,
        start_time=datetime(2026, 11, 9, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 9, 10, 30, tzinfo=UTC),
        status=AppointmentStatus.SCHEDULED,
    )


def test_save_appointment(appointment_repository, appointment):
    saved_appointment = appointment_repository.save(appointment)

    assert saved_appointment.id is not None
    assert saved_appointment.id == 1
    assert saved_appointment.patient_id == 1
    assert saved_appointment.status == AppointmentStatus.SCHEDULED


def test_find_by_id_returns_appointment(appointment_repository, appointment):
    saved_appointment = appointment_repository.save(appointment)
    retrieved_appointment = appointment_repository.find_by_id(saved_appointment.id)

    assert retrieved_appointment is not None
    assert retrieved_appointment.id == saved_appointment.id
    assert retrieved_appointment.patient_id == saved_appointment.patient_id
    assert retrieved_appointment.start_time == saved_appointment.start_time
    assert retrieved_appointment.end_time == saved_appointment.end_time
    assert retrieved_appointment.status == saved_appointment.status


def test_find_by_id_returns_none_when_not_found(appointment_repository):
    retrieved_appointment = appointment_repository.find_by_id(999)

    assert retrieved_appointment is None


def test_find_by_patient_id_returns_all_patient_appointments(
    appointment_repository, appointment
):
    first_appointment = appointment_repository.save(appointment)

    second_appointment = Appointment(
        id=None,
        patient_id=1,
        start_time=datetime(2026, 11, 10, 11, 0, tzinfo=UTC),
        end_time=datetime(2026, 11, 10, 11, 30, tzinfo=UTC),
        status=AppointmentStatus.SCHEDULED,
    )

    appointment_repository.save(second_appointment)

    appointments = appointment_repository.find_by_patient_id(1)

    assert len(appointments) == 2
    assert appointments[0].id == first_appointment.id
    assert appointments[1].start_time == second_appointment.start_time


def test_find_by_patient_id_returns_empty_list_when_no_appointments(
    appointment_repository,
):
    appointments = appointment_repository.find_by_patient_id(1)

    assert appointments == []


def test_update_appointment(appointment_repository, appointment):
    saved_appointment = appointment_repository.save(appointment)

    saved_appointment.start_time = datetime(2026, 11, 9, 14, 0, tzinfo=UTC)
    saved_appointment.end_time = datetime(2026, 11, 9, 14, 30, tzinfo=UTC)

    saved_appointment.status = AppointmentStatus.ATTENDED

    updated_appointment = appointment_repository.update(saved_appointment)

    assert updated_appointment is not None
    assert updated_appointment.id == saved_appointment.id
    assert updated_appointment.start_time == saved_appointment.start_time
    assert updated_appointment.end_time == saved_appointment.end_time
    assert updated_appointment.status == AppointmentStatus.ATTENDED


def test_update_appointment_returns_none_when_id_is_none(
    appointment_repository,
    appointment,
):

    updated_appointment = appointment_repository.update(appointment)

    assert updated_appointment is None


def test_update_appointment_returns_none_when_not_found(
    appointment_repository,
    appointment,
):

    appointment.id = 999

    updated_appointment = appointment_repository.update(appointment)

    assert updated_appointment is None


def test_update_appointment_persists_changes(
    appointment_repository,
    appointment,
):

    saved_appointment = appointment_repository.save(appointment)

    saved_appointment.status = AppointmentStatus.ATTENDED

    appointment_repository.update(saved_appointment)

    retrieved_appointment = appointment_repository.find_by_id(saved_appointment.id)

    assert retrieved_appointment is not None
    assert retrieved_appointment.status == AppointmentStatus.ATTENDED


def test_delete_appointment(appointment_repository, appointment):
    saved_appointment = appointment_repository.save(appointment)

    result = appointment_repository.delete_by_id(saved_appointment.id)

    assert result is True
    assert appointment_repository.find_by_id(saved_appointment.id) is None


def test_delete_appointment_returns_false_when_not_found(
    appointment_repository,
):

    result = appointment_repository.delete_by_id(999)

    assert result is False


def test_save_appointment_fails_when_patient_does_not_exist(
    appointment_repository, appointment
):
    appointment.patient_id = 999

    with pytest.raises(sqlite3.IntegrityError):
        appointment_repository.save(appointment)
