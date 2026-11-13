from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient

from panda.api.dependencies.patient_dependencies import (
    get_patient_service,
)
from panda.api.main import app

client = TestClient(app)


def test_create_patient_success(monkeypatch) -> None:
    patient_service = SimpleNamespace(
        register_patient=lambda *args: SimpleNamespace(
            id=1,
            nhs_number=args[0],
            first_name=args[1],
            last_name=args[2],
            date_of_birth=args[3],
            postcode=args[4],
        )
    )

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    payload = {
        "nhs_number": "9434765919",
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1990-05-15",
        "postcode": "SW1A 1AA",
    }

    response = client.post("/patients", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["first_name"] == "John"
    assert response.json()["last_name"] == "Smith"
    assert response.json()["nhs_number"] == "9434765919"


def test_create_patient_invalid_request() -> None:
    payload = {
        "nhs_number": "9434765919",
        "first_name": "John",
        "date_of_birth": "1990-05-15",
        "postcode": "SW1A 1AA",
    }

    response = client.post("/patients", json=payload)

    assert response.status_code == 422


def test_create_patient_duplicate_nhs_number(monkeypatch) -> None:
    def register_patient(*args):
        raise ValueError("Patient with this NHS number already exists")

    patient_service = SimpleNamespace(register_patient=register_patient)

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    payload = {
        "nhs_number": "9434765919",
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1990-05-15",
        "postcode": "SW1A 1AA",
    }

    response = client.post("/patients", json=payload)

    assert response.status_code == 409
    assert response.json() == {"detail": "Patient with this NHS number already exists"}


def test_get_all_patients(monkeypatch) -> None:
    patients = [
        SimpleNamespace(
            id=1,
            nhs_number="9434765919",
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1990, 5, 15),
            postcode="SW1A 1AA",
        ),
        SimpleNamespace(
            id=2,
            nhs_number="9876543210",
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date(1985, 8, 20),
            postcode="M1 1AE",
        ),
    ]

    patient_service = SimpleNamespace(get_all_patients=lambda: patients)

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    response = client.get("/patients")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["first_name"] == "John"
    assert response.json()[1]["first_name"] == "Jane"


def test_get_patient_by_id_success(monkeypatch) -> None:
    patient = SimpleNamespace(
        id=1,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 15),
        postcode="SW1A 1AA",
    )

    patient_service = SimpleNamespace(get_patient_by_id=lambda patient_id: patient)

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    response = client.get("/patients/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["first_name"] == "John"


def test_get_patient_by_id_not_found(monkeypatch) -> None:
    patient_service = SimpleNamespace(get_patient_by_id=lambda patient_id: None)

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    response = client.get("/patients/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Patient not found"}


def test_update_patient_postcode_success(monkeypatch) -> None:
    patient = SimpleNamespace(
        id=1,
        nhs_number="9434765919",
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1990, 5, 15),
        postcode="M1 1AE",
    )

    patient_service = SimpleNamespace(
        get_patient_by_id=lambda patient_id: patient,
        update_patient_postcode=lambda patient_id, postcode: patient,
    )

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    response = client.patch(
        "/patients/1",
        json={"postcode": "M1 1AE"},
    )

    assert response.status_code == 200
    assert response.json()["postcode"] == "M1 1AE"


def test_update_patient_postcode_not_found(monkeypatch) -> None:
    patient_service = SimpleNamespace(
        get_patient_by_id=lambda patient_id: None,
    )

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    response = client.patch(
        "/patients/999",
        json={"postcode": "M1 1AE"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Patient not found"}


def test_delete_patient_success(monkeypatch) -> None:
    patient_service = SimpleNamespace(
        delete_patient=lambda patient_id: True,
    )

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    response = client.delete("/patients/1")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_patient_not_found(monkeypatch) -> None:
    patient_service = SimpleNamespace(
        delete_patient=lambda patient_id: False,
    )

    monkeypatch.setitem(
        app.dependency_overrides,
        get_patient_service,
        lambda: patient_service,
    )

    response = client.delete("/patients/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Patient not found"}
