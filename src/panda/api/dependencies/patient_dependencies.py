from panda.database.schema_initializer import initialise_schema
from panda.repositories.sqlite_patient_repository import (
    SQLitePatientRepository,
)
from panda.services.patient_service import PatientService


def get_patient_service() -> PatientService:
    """Provide a PatientService instance for API endpoints."""

    initialise_schema()

    patient_repository = SQLitePatientRepository()

    return PatientService(patient_repository)
