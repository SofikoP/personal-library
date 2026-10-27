import pytest

from src.init_db import initialize_database
from src.database import get_connection


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test_library.db"
    initialize_database(path)
    return path


@pytest.fixture
def connection(db_path):
    connection = get_connection(db_path)
    yield connection
    connection.close()