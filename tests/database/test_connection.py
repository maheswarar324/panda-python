import sqlite3

import pytest

from panda.database.connection import get_connection


@pytest.fixture
def database_path(tmp_path):
    path = tmp_path / "test.db"

    connection = sqlite3.connect(path)

    connection.execute(
        """
        CREATE TABLE patients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE appointments (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
        """
    )

    connection.commit()
    connection.close()

    return path


def test_connection_commits_successful_transaction(database_path):
    with get_connection(database_path) as connection:
        connection.execute(
            "INSERT INTO patients (name) VALUES (?)",
            ("John",),
        )

    verification_connection = sqlite3.connect(database_path)

    try:
        row = verification_connection.execute("SELECT name FROM patients").fetchone()

        assert row[0] == "John"
    finally:
        verification_connection.close()


def test_connection_rolls_back_failed_transaction(database_path):
    with pytest.raises(RuntimeError), get_connection(database_path) as connection:
        connection.execute(
            "INSERT INTO patients (name) VALUES (?)",
            ("John",),
        )

        raise RuntimeError("Simulated database failure")

    verification_connection = sqlite3.connect(database_path)

    try:
        row = verification_connection.execute("SELECT name FROM patients").fetchone()

        assert row is None
    finally:
        verification_connection.close()


def test_connection_enables_foreign_keys(database_path):
    with get_connection(database_path) as connection:
        result = connection.execute("PRAGMA foreign_keys").fetchone()

        assert result[0] == 1


def test_connection_rejects_invalid_foreign_key(database_path):
    with (
        pytest.raises(sqlite3.IntegrityError),
        get_connection(database_path) as connection,
    ):
        connection.execute(
            """
            INSERT INTO appointments (patient_id)
            VALUES (999)
            """
        )


def test_connection_disables_foreign_keys_when_configured(database_path):
    with get_connection(database_path, foreign_keys=False) as connection:
        result = connection.execute("PRAGMA foreign_keys").fetchone()

        assert result[0] == 0


def test_connection_is_closed_after_successful_transaction(database_path):
    with get_connection(database_path) as connection:
        connection.execute("SELECT 1")

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


def test_connection_is_closed_after_failed_transaction(database_path):
    with (
        pytest.raises(RuntimeError),
        get_connection(database_path) as connection,
    ):
        connection.execute("SELECT 1")
        raise RuntimeError("Simulated failure")

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")
