from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Configuration directory
CONFIG_DIRECTORY = PROJECT_ROOT / "config"

# SQL directory
SQL_DIRECTORY = PROJECT_ROOT / "sql"

# SQL files
SCHEMA_FILE = SQL_DIRECTORY / "create_schema.sql"
PATIENT_QUERIES_FILE = SQL_DIRECTORY / "patient_queries.sql"
APPOINTMENT_QUERIES_FILE = SQL_DIRECTORY / "appointment_queries.sql"

# Database
DATABASE_FILE = PROJECT_ROOT / "panda.db"
