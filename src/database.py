import sqlite3
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "library.db"
SQL_PATH = PROJECT_ROOT / "sql" / "create_tables.sql"


def get_connection(path=DB_PATH):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction(path=DB_PATH):
    connection = get_connection(path)

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()