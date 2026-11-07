import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def get_connection(
    database_path: str | Path,
    timeout: int = 30,
    foreign_keys: bool = True,
):
    connection = sqlite3.connect(
        database_path,
        timeout=timeout,
    )
    connection.row_factory = sqlite3.Row

    if foreign_keys:
        connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except:
        connection.rollback()
        raise
    finally:
        connection.close()


# 3. Understand the new implementation
# Python	Purpose
# @contextmanager	Creates a context manager from a generator
# yield connection	Makes the connection available to the caller
# commit()	Saves successful database changes
# rollback()	Reverts changes after an exception
# finally	Always executes cleanup
# close()	Releases the database connection

# 4. Java Spring Boot comparison
# Python SQLite	Java equivalent
# @contextmanager	Resource-management abstraction
# yield connection	Providing a resource to the caller
# commit()	Transaction commit
# rollback()	Transaction rollback
# finally: close()	Resource cleanup / try-with-resources

# ou've just encountered an important Python distinction:
# a context manager doesn't necessarily mean automatic resource closure.
# Its behaviour depends on how that context manager is implemented.
