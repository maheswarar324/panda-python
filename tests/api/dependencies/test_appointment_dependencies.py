from panda.api.dependencies.appointment_dependencies import (
    get_appointment_service,
)
from panda.services.appointment_service import AppointmentService


def test_get_appointment_service_returns_appointment_service():
    service = get_appointment_service()

    assert isinstance(service, AppointmentService)
