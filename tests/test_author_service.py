import sqlite3

import pytest

from src import author_service


def test_create_author(connection):
    author_id = author_service.create_author(
        connection, country="UK", name="J. K. Rowling", language="en"
    )

    assert author_service.find_author_by_name(connection, "J. K. Rowling") == author_id


def test_add_author_name_in_another_language(connection):
    author_id = author_service.create_author(
        connection, country="Russia", name="Антон Чехов", language="ru"
    )

    author_service.add_author_name(connection, author_id, "Anton Chekhov", "en")

    assert author_service.find_author_by_name(connection, "Anton Chekhov") == author_id


def test_second_name_in_same_language_is_rejected(connection):
    author_id = author_service.create_author(
        connection, country="Russia", name="Антон Чехов", language="ru"
    )

    with pytest.raises(sqlite3.IntegrityError):
        author_service.add_author_name(connection, author_id, "А. П. Чехов", "ru")
