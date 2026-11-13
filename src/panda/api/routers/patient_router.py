from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from panda.api.dependencies.patient_dependencies import (
    get_patient_service,
)
from panda.api.schemas.patient_schemas import (
    PatientCreate,
    PatientPostcodeUpdate,
    PatientResponse,
)
from panda.services.patient_service import PatientService

# Router for all patient-related API endpoints.
router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_data: PatientCreate,
    patient_service: Annotated[
        PatientService,
        Depends(get_patient_service),
    ],
) -> PatientResponse:
    """Register a new patient."""

    try:
        patient = patient_service.register_patient(
            patient_data.nhs_number,
            patient_data.first_name,
            patient_data.last_name,
            patient_data.date_of_birth,
            patient_data.postcode,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return PatientResponse.model_validate(patient)


@router.get(
    "",
    response_model=list[PatientResponse],
)
def get_all_patients(
    patient_service: Annotated[
        PatientService,
        Depends(get_patient_service),
    ],
) -> list[PatientResponse]:
    """Retrieve all registered patients."""

    patients = patient_service.get_all_patients()

    return [PatientResponse.model_validate(patient) for patient in patients]


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient_by_id(
    patient_id: int,
    patient_service: Annotated[
        PatientService,
        Depends(get_patient_service),
    ],
) -> PatientResponse:
    """Retrieve a patient by ID."""

    patient = patient_service.get_patient_by_id(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return PatientResponse.model_validate(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient_postcode(
    patient_id: int,
    patient_data: PatientPostcodeUpdate,
    patient_service: Annotated[
        PatientService,
        Depends(get_patient_service),
    ],
) -> PatientResponse:
    """Update a patient's postcode."""

    existing_patient = patient_service.get_patient_by_id(patient_id)

    if existing_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    try:
        updated_patient = patient_service.update_patient_postcode(
            patient_id,
            patient_data.postcode,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return PatientResponse.model_validate(updated_patient)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: int,
    patient_service: Annotated[
        PatientService,
        Depends(get_patient_service),
    ],
) -> None:
    """Delete a patient by ID."""

    deleted = patient_service.delete_patient(patient_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
