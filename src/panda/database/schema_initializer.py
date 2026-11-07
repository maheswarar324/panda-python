from pathlib import Path

from panda.config.paths import DATABASE_FILE
from panda.database.connection import get_connection
from panda.database.schema_loader import load_schema


def initialise_schema(
    database_path: str | Path = DATABASE_FILE,
) -> None:
    with get_connection(database_path) as connection:
        schema_sql = load_schema()
        connection.executescript(schema_sql)
