from datetime import date

from pydantic import BaseModel, ConfigDict


class PatientCreate(BaseModel):
    """Schema for registering a new patient."""

    nhs_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    postcode: str


class PatientResponse(BaseModel):
    """Schema for returning patient information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nhs_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    postcode: str


class PatientPostcodeUpdate(BaseModel):
    """Schema for updating a patient's postcode."""

    postcode: str
