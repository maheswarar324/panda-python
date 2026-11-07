import sqlite3
from datetime import date

from panda.config.paths import DATABASE_FILE, PATIENT_QUERIES_FILE
from panda.database.connection import get_connection
from panda.database.sql_loader import load_sql_queries
from panda.models.patient import Patient


class SQLitePatientRepository:
    def __init__(self, database_path: str = DATABASE_FILE):
        self._database_path = database_path
        self._queries = load_sql_queries(PATIENT_QUERIES_FILE)

    def _get_connection(self):
        return get_connection(self._database_path)

    def save(self, patient: Patient) -> Patient:

        with self._get_connection() as connection:
            cursor = connection.execute(
                self._queries["INSERT"],
                (
                    patient.nhs_number,
                    patient.first_name,
                    patient.last_name,
                    patient.date_of_birth.isoformat(),
                    patient.postcode,
                ),
            )

            patient.id = cursor.lastrowid

        return patient

    def find_by_id(self, patient_id: int) -> Patient | None:

        with self._get_connection() as connection:
            row = connection.execute(
                self._queries["SELECT_BY_ID"],
                (patient_id,),
            ).fetchone()

        if row is None:
            return None

        return self.sql_row_to_patient(row=row)

    def find_all(self) -> list[Patient]:
        with self._get_connection() as connection:
            rows = connection.execute(self._queries["SELECT_ALL"]).fetchall()

        # is called a list comprehension. It converts every database row into a Patient object.
        return [self.sql_row_to_patient(row=row) for row in rows]

    def update(self, patient: Patient) -> Patient | None:

        with self._get_connection() as connection:
            cursor = connection.execute(
                self._queries["UPDATE"],
                (
                    patient.nhs_number,
                    patient.first_name,
                    patient.last_name,
                    patient.date_of_birth.isoformat(),
                    patient.postcode,
                    patient.id,
                ),
            )

            if cursor.rowcount == 0:
                return None

            row = connection.execute(
                self._queries["SELECT_BY_ID"],
                (patient.id,),
            ).fetchone()

        if row is None:
            return None

        return self.sql_row_to_patient(row=row)

    def sql_row_to_patient(self, row: sqlite3.Row) -> Patient:

        return Patient(
            id=row["id"],
            nhs_number=row["nhs_number"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            date_of_birth=date.fromisoformat(row["date_of_birth"]),
            postcode=row["postcode"],
        )

    def delete_by_id(self, patient_id: int) -> bool:
        with self._get_connection() as connection:
            cursor = connection.execute(
                self._queries["DELETE_BY_ID"],
                (
                    patient_id,
                ),  # Tuple with one element. SQLite expects the parameters as a sequence, so we pass a tuple.
            )

            return cursor.rowcount > 0

    def find_by_nhs_number(self, nhs_number: str) -> Patient | None:
        with self._get_connection() as connection:
            row = connection.execute(
                self._queries["SELECT_BY_NHS_NUMBER"],
                (nhs_number,),
            ).fetchone()

        if row is None:
            return None

        return self.sql_row_to_patient(row=row)
