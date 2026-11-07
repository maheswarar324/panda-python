from panda.models.patient import Patient


class FakePatientRepository:
    def __init__(self):
        self.patients: dict[int, Patient] = {}

    def save(self, patient: Patient) -> Patient:
        patient.id = len(self.patients) + 1
        self.patients[patient.id] = patient
        return patient

    def find_by_id(self, patient_id: int) -> Patient | None:
        return self.patients.get(patient_id)

    def find_by_nhs_number(self, nhs_number: str) -> Patient | None:
        for patient in self.patients.values():
            if patient.nhs_number == nhs_number:
                return patient
        return None

    def update(self, patient: Patient) -> Patient:
        if patient.id is None or patient.id not in self.patients:
            raise ValueError("Patient not found")

        self.patients[patient.id] = patient
        return patient
