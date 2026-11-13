from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from panda.api.dependencies.appointment_dependencies import (
    get_appointment_service,
)
from panda.api.schemas.appointment_schemas import (
    AppointmentCreate,
    AppointmentReschedule,
    AppointmentResponse,
    AppointmentStatusUpdate,
)
from panda.exceptions.invalid_appointment_state_error import (
    InvalidAppointmentStateError,
)
from panda.services.appointment_service import AppointmentService

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    appointment_data: AppointmentCreate,
    appointment_service: Annotated[
        AppointmentService,
        Depends(get_appointment_service),
    ],
) -> AppointmentResponse:
    """Book a new appointment."""

    try:
        appointment = appointment_service.book_appointment(
            appointment_data.patient_id,
            appointment_data.start_time,
            appointment_data.end_time,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Patient not found":
            status_code = status.HTTP_404_NOT_FOUND
        elif "already has an appointment" in message:
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc

    return AppointmentResponse.model_validate(appointment)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
    appointment_id: int,
    appointment_service: Annotated[
        AppointmentService,
        Depends(get_appointment_service),
    ],
) -> AppointmentResponse:
    """Retrieve an appointment by ID."""

    appointment = appointment_service.get_appointment_by_id(appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
)
def update_appointment_status(
    appointment_id: int,
    appointment_data: AppointmentStatusUpdate,
    appointment_service: Annotated[
        AppointmentService,
        Depends(get_appointment_service),
    ],
) -> AppointmentResponse:
    """Update an appointment's status."""

    appointment = appointment_service.update_appointment_status(
        appointment_id,
        appointment_data.status,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
def cancel_appointment(
    appointment_id: int,
    appointment_service: Annotated[
        AppointmentService,
        Depends(get_appointment_service),
    ],
) -> AppointmentResponse:
    """Cancel an appointment."""

    appointment = appointment_service.cancel_appointment(appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
)
def reschedule_appointment(
    appointment_id: int,
    appointment_data: AppointmentReschedule,
    appointment_service: Annotated[
        AppointmentService,
        Depends(get_appointment_service),
    ],
) -> AppointmentResponse:
    """Reschedule an existing appointment."""

    try:
        appointment = appointment_service.reschedule_appointment(
            appointment_id,
            appointment_data.start_time,
            appointment_data.end_time,
        )
    except InvalidAppointmentStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        message = str(exc)

        if "already has an appointment" in message:
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return AppointmentResponse.model_validate(appointment)
