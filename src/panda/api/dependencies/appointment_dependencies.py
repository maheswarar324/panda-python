from panda.services.appointment_service import AppointmentService


def get_appointment_service() -> AppointmentService:
    """Provide an appointment service instance."""
    return AppointmentService()
