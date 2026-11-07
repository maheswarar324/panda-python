import sqlite3
from datetime import datetime
from pathlib import Path

from panda.config.paths import APPOINTMENT_QUERIES_FILE, DATABASE_FILE
from panda.database.connection import get_connection
from panda.database.sql_loader import load_sql_queries
from panda.models.appointment import Appointment, AppointmentStatus


class SQLiteAppointmentRepository:
    def __init__(
        self,
        database_path: str | Path = DATABASE_FILE,
    ) -> None:
        self._database_path = database_path
        self._queries = load_sql_queries(APPOINTMENT_QUERIES_FILE)

    def save(self, appointment: Appointment) -> Appointment:
        with get_connection(self._database_path) as connection:
            cursor = connection.execute(
                self._queries["INSERT"],
                (
                    appointment.patient_id,
                    appointment.start_time.isoformat(),
                    appointment.end_time.isoformat(),
                    appointment.status.value,
                ),
            )

            appointment_id = cursor.lastrowid

        saved_appointment = self.find_by_id(appointment_id)

        if saved_appointment is None:
            raise RuntimeError("Could not retrieve the saved appointment")

        return saved_appointment

    def find_by_id(self, appointment_id: int) -> Appointment | None:
        with get_connection(self._database_path) as connection:
            row = connection.execute(
                self._queries["SELECT_BY_ID"],
                (appointment_id,),
            ).fetchone()

        if row is None:
            return None

        return self._map_row_to_appointment(row)

    def find_by_patient_id(self, patient_id: int) -> list[Appointment]:
        with get_connection(self._database_path) as connection:
            rows = connection.execute(
                self._queries["SELECT_BY_PATIENT_ID"],
                (patient_id,),
            ).fetchall()

        return [self._map_row_to_appointment(row) for row in rows]

    def update(self, appointment: Appointment) -> Appointment | None:
        if appointment.id is None:
            return None

        with get_connection(self._database_path) as connection:
            cursor = connection.execute(
                self._queries["UPDATE"],
                (
                    appointment.patient_id,
                    appointment.start_time.isoformat(),
                    appointment.end_time.isoformat(),
                    appointment.status.value,
                    appointment.id,
                ),
            )

            if cursor.rowcount == 0:
                return None

        return self.find_by_id(appointment.id)

    def delete_by_id(self, appointment_id: int) -> bool:
        with get_connection(self._database_path) as connection:
            cursor = connection.execute(
                self._queries["DELETE_BY_ID"], (appointment_id,)
            )

        return cursor.rowcount > 0

    @staticmethod
    def _map_row_to_appointment(row: sqlite3.Row) -> Appointment:
        return Appointment(
            id=row["id"],
            patient_id=row["patient_id"],
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]),
            status=AppointmentStatus(row["status"]),
        )
