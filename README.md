# PANDA Python

**Patient Appointment and Administration System**

PANDA Python is a learning project that implements a patient and appointment management system using Python, SQLite and modern Python development practices.

The project is a Python implementation of an earlier Java PANDA application. Its objective is to reproduce the core functionality while adopting Pythonic approaches to application design, data modelling, repository abstractions, configuration management, REST API development and testing.

## Objectives

- Build a maintainable Python application using clean separation of responsibilities.
- Understand Python equivalents of Java and Spring Boot concepts.
- Implement repository abstractions and dependency inversion.
- Practise database operations using SQLite and parameterised SQL.
- Develop confidence with Python type hints, dataclasses, protocols and context managers.
- Develop REST APIs using FastAPI and Pydantic.
- Establish automated testing and code-quality practices.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13+ | Application development |
| FastAPI | REST API development |
| Pydantic | Request validation and API schemas |
| SQLite | Relational database |
| `sqlite3` | Database connectivity |
| `uv` | Python project and dependency management |
| `pytest` | Automated testing |
| `ruff` | Linting and formatting |
| `dataclasses` | Domain modelling |
| `typing.Protocol` | Repository abstractions |

## Features

### Patient Management

- Register patients.
- Retrieve patients by ID.
- Retrieve patients by NHS number.
- Retrieve all patients.
- Update patient information.
- Delete patients.
- Validate patient information, including NHS numbers and UK postcodes.
- Prevent duplicate NHS numbers.

### Appointment Management

- Create appointments for patients.
- Retrieve appointments by ID.
- Retrieve appointments by patient.
- Update and reschedule appointments.
- Cancel appointments.
- Manage appointment lifecycle states.
- Validate appointment time ranges and timezone information.
- Prevent invalid appointment state transitions.
- Detect scheduling conflicts.
- Enforce patient relationships through database foreign keys.

### Appointment Lifecycle

Appointments support the following states:

- `SCHEDULED`
- `ATTENDED`
- `MISSED`
- `CANCELLED`

Business rules control permitted appointment state transitions.

## Architecture

The application follows a layered architecture with separation between API, domain models, services, repositories and database infrastructure.

```text
src/
└── panda/
    ├── api/
    │   ├── dependencies/
    │   ├── routers/
    │   ├── schemas/
    │   └── main.py
    ├── config/
    │   ├── config_loader.py
    │   ├── database_config.py
    │   └── paths.py
    ├── database/
    │   ├── connection.py
    │   ├── schema_initializer.py
    │   ├── schema_loader.py
    │   ├── sql_loader.py
    │   └── ...
    ├── exceptions/
    ├── models/
    │   ├── patient.py
    │   └── appointment.py
    ├── repositories/
    │   ├── patient_repository_protocol.py
    │   ├── appointment_repository_protocol.py
    │   ├── sqlite_patient_repository.py
    │   ├── sqlite_appointment_repository.py
    │   └── ...
    ├── services/
    │   ├── patient_service.py
    │   └── appointment_service.py
    └── validators/

tests/
├── api/
│   ├── dependencies/
│   ├── routers/
│   └── schemas/
├── config/
├── database/
├── integration/
├── models/
├── repositories/
├── services/
└── validators/
```

## Design Principles

### Repository Pattern

Repository abstractions separate business logic from database implementation.

Python `Protocol` is used to define repository contracts, allowing services to depend on abstractions rather than concrete implementations.

### Domain Models

Python dataclasses represent domain entities such as `Patient` and `Appointment`.

Validation and domain rules are incorporated into the models and services where appropriate.

### API Layer

FastAPI routers expose patient and appointment functionality through REST endpoints.

Pydantic schemas handle API request validation and data representation.

FastAPI dependencies provide the wiring between API endpoints and application services.

### Database Management

SQLite provides relational persistence.

Database responsibilities are separated into:

- Connection management.
- Schema initialisation.
- SQL query loading.
- Repository implementations.

SQL statements are maintained separately from repository implementation code and executed using parameterised queries.

### Configuration Management

Application configuration is externalised through properties files and environment-specific settings.

Supported environments:

- `dev`
- `test`
- `prod`

The `PANDA_ENV` environment variable controls the selected configuration environment.

### Testing

Automated tests are written using pytest.

The test suite covers:

- Domain models.
- Validation.
- Repository implementations.
- Database operations.
- Service business logic.
- Integration workflows.
- API endpoints and dependencies.

Tests use temporary SQLite databases and mocks where appropriate to isolate behaviour.

## Getting Started

### Prerequisites

- Python 3.13 or later.
- UV package manager.

### Clone the repository

```bash
git clone <repository-url>
cd panda-python
```

### Install dependencies

```bash
uv sync
```

### Select the environment

PowerShell:

```powershell
$env:PANDA_ENV = "dev"
```

### Run the application

```bash
uv run uvicorn panda.api.main:app --reload
```

### API documentation

Once the application is running:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Run the tests

```bash
uv run pytest -v
```

### Run Ruff linting

```bash
uv run ruff check .
```

### Check code formatting

```bash
uv run ruff format --check .
```

### Apply code formatting

```bash
uv run ruff format .
```

## Development Approach

PANDA Python is developed incrementally, with an emphasis on understanding the reasoning behind each implementation decision.

The project also provides an opportunity to compare Java and Python approaches to:

- Object-oriented programming.
- Interfaces and protocols.
- Dependency injection.
- Encapsulation.
- Exception handling.
- Database transactions.
- Automated testing.
- Application architecture.

The objective is not to reproduce Spring Boot in Python, but to understand how established software engineering principles translate into Python and where Python offers different or simpler approaches.

## Future Enhancements

Potential areas for further development include:

- Database migrations and version management.
- PostgreSQL support.
- TOML-based configuration.
- Additional appointment business rules.
- Improved application-level logging and observability.
- Authentication and authorisation.
- Containerisation and deployment.
- CI/CD automation.
- Agentic AI integration.

## Project Status

**Core implementation and initial quality validation complete.**

Latest validation results:

| Validation | Result |
|---|---|
| Automated tests | 187 passed |
| Ruff linting | All checks passed |
| Ruff formatting | 63 files already formatted |
| Dependency consistency | Verified |
| Dependency lockfile | Up to date |

PANDA Python is primarily an educational and portfolio project focused on practical Python software engineering and translating established Java development experience into the Python ecosystem.