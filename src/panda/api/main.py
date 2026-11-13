from fastapi import FastAPI, status

from panda.api.routers.appointment_router import (
    router as appointment_router,
)
from panda.api.routers.patient_router import (
    router as patient_router,
)

app = FastAPI(
    title="PANDA API",
    description="Patient Appointment and Administration API",
    version="1.0.0",
)


@app.get("/", status_code=status.HTTP_200_OK)
def root() -> dict[str, str]:
    return {"message": "Welcome to PANDA API"}


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(patient_router)
app.include_router(appointment_router)


# Understanding the Java equivalent
# FastAPI	Spring Boot
# FastAPI()	@SpringBootApplication
# app.get("/")	@GetMapping("/")
# def root()	Controller method
# return dict	Returning a response object

# Notice that FastAPI automatically converts Python dictionaries into JSON responses.

# to run: uv run uvicorn panda.api.main:app --reload
# Explanation:
# - panda.api.main – Python module containing our application.
# - app – FastAPI application instance.
# - --reload – Automatically restarts the server when code changes.

# url to access: http://127.0.0.1:8000/
# health check url: http://127.0.0.1:8000/health
# automatically generated Swagger UI documentation.: http://127.0.0.1:8000/docs
