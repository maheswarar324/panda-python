from datetime import date

from panda.models.patient import Patient
from panda.repositories.patient_repository import PatientRepository
from panda.repositories.patient_repository_protocol import PatientRepositoryProtocol


class PatientService:
    def __init__(self, patient_repository: PatientRepositoryProtocol | None = None):
        self._patient_repository = (
            patient_repository
            if patient_repository is not None
            else PatientRepository()
        )

    def register_patient(
        self,
        nhs_number: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        postcode: str,
    ) -> Patient:
        patient = Patient(
            id=None,
            nhs_number=nhs_number,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            postcode=postcode,
        )

        existing_patient = self._patient_repository.find_by_nhs_number(nhs_number)

        if existing_patient is not None:
            raise ValueError("Patient with this NHS number already exists")

        return self._patient_repository.save(patient)

    def get_patient_by_id(self, patient_id: int) -> Patient | None:
        return self._patient_repository.find_by_id(patient_id)

    def get_patient_by_nhs_number(
        self,
        nhs_number: str,
    ) -> Patient | None:
        return self._patient_repository.find_by_nhs_number(nhs_number)

    def update_patient_postcode(
        self,
        patient_id: int,
        postcode: str,
    ) -> Patient:
        patient = self._patient_repository.find_by_id(patient_id)

        if patient is None:
            raise ValueError("Patient not found")

        updated_patient = Patient(
            id=patient.id,
            nhs_number=patient.nhs_number,
            first_name=patient.first_name,
            last_name=patient.last_name,
            date_of_birth=patient.date_of_birth,
            postcode=postcode,
        )

        return self._patient_repository.update(updated_patient)

    def delete_patient(self, patient_id: int) -> bool:
        return self._patient_repository.delete_by_id(patient_id)
