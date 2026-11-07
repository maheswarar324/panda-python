from panda.models.patient import Patient


class PatientRepository:
    def __init__(self):
        self._patients: dict[int, Patient] = {}
        self._next_id = 1

    def save(self, patient: Patient) -> Patient:
        existing_patient = self.find_by_nhs_number(patient.nhs_number)

        if existing_patient is not None:
            raise ValueError("Patient with this NHS number already exists")

        patient.id = self._next_id
        self._patients[self._next_id] = patient
        self._next_id += 1

        return patient

    def find_by_id(self, patient_id: int) -> Patient | None:
        return self._patients.get(patient_id)

    def find_by_nhs_number(self, nhs_number: str) -> Patient | None:
        for patient in self._patients.values():
            if patient.nhs_number == nhs_number:
                return patient

        return None

    def update(self, patient: Patient) -> Patient:
        if patient.id is None or patient.id not in self._patients:
            raise ValueError("Patient not found")

        self._patients[patient.id] = patient

        return patient

    def delete_by_id(self, patient_id: int) -> bool:
        if patient_id not in self._patients:
            return False

        del self._patients[patient_id]
        return True
