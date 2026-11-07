# PANDA Python

**Patient Appointment and Administration System**

PANDA Python is a learning project that implements a patient and appointment management system using Python, SQLite and modern Python development practices.

The project is a Python implementation of an earlier Java PANDA application. Its objective is to reproduce the core functionality while adopting Pythonic approaches to application design, data modelling, repository abstractions, configuration management and testing.

## Objectives

- Build a maintainable Python application using clean separation of responsibilities.
- Understand Python equivalents of Java and Spring Boot concepts.
- Implement repository abstractions and dependency inversion.
- Practise database operations using SQLite and parameterised SQL.
- Develop confidence with Python type hints, dataclasses, protocols and context managers.
- Establish automated testing and code-quality practices.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13+ | Application development |
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
- Validate patient information.
- Prevent duplicate NHS numbers.

### Appointment Management

- Create and manage appointments.
- Associate appointments with patients.
- Retrieve appointment information.
- Maintain appointment status.
- Enforce patient relationships through database foreign keys.

## Architecture

The application follows a layered architecture with separation between domain models, services, repositories and database infrastructure.

```text
src/
└── panda/
    ├── config/
    │   ├── paths.py
    │   └── ...
    ├── database/
    │   ├── connection.py
    │   ├── schema_initializer.py
    │   ├── sql_loader.py
    │   └── ...
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
        └── ...

tests/
├── repositories/
├── services/
├── models/
├── validators/
├── database/
└── ...
```

*The structure above is a high-level overview; individual files may evolve as development continues.*

## Design Principles

### Repository Pattern

Repository abstractions separate business logic from database implementation.

Python `Protocol` is used to define repository contracts, allowing services to depend on abstractions rather than concrete implementations.

### Domain Models

Python dataclasses represent domain entities such as `Patient` and `Appointment`.

Validation is incorporated into the domain model where appropriate.

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

The `PANDA_ENV` environment variable controls the selected configuration environment.

### Testing

Automated tests are written using pytest.

The test suite covers domain models, validation, repositories, database operations and services.

Tests use temporary SQLite databases and mocks where appropriate to isolate behaviour.

## Getting Started

### Prerequisites

- Python 3.13 or later.
- uv package manager.

### Clone the repository

```bash
git clone <repository-url>
cd panda-python
```

### Install dependencies

```bash
uv sync
```

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

## Future Enhancements

Potential areas for further development include:

- Database migrations and version management.
- Additional appointment business rules.
- REST API integration.
- Improved application-level logging.
- Additional integration tests.
- Agentic AI integration.

## Project Status

The core patient and appointment domain, repository and service implementations are under development completion and testing.

**PANDA Python is primarily an educational and portfolio project focused on practical Python software engineering.**
