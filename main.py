from datetime import date

from panda.config.config_loader import load_config
from panda.database.schema_initializer import initialise_schema
from panda.repositories.sqlite_patient_repository import SQLitePatientRepository
from panda.services.patient_service import PatientService


def create_patient_service() -> PatientService:
    initialise_schema()

    patient_repository = SQLitePatientRepository()

    return PatientService(patient_repository)


def main():
    validate_sql()
    validate_config()


def validate_sql():
    patient_service = create_patient_service()

    nhs_number = "9434765919"

    patient = patient_service.get_patient_by_nhs_number(nhs_number)

    if patient is None:
        patient = patient_service.register_patient(
            nhs_number=nhs_number,
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 5, 20),
            postcode="SW1A 1AA",
        )

        print("New patient registered successfully!")
    else:
        print("Existing patient retrieved from database!")

    print(f"Patient ID: {patient.id}")
    print(f"Name: {patient.first_name} {patient.last_name}")
    print(f"NHS Number: {patient.nhs_number}")
    print(f"Postcode: {patient.postcode}")


def validate_config():
    config = load_config()

    timeout = config.getint("database", "timeout")
    foreign_keys = config.getboolean("database", "foreign_keys")
    show_sql = config.getboolean("database", "show_sql")

    print(type(timeout), timeout)
    print(type(foreign_keys), foreign_keys)
    print(type(show_sql), show_sql)


if __name__ == "__main__":
    main()
