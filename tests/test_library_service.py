import sqlite3

import pytest

from src import library_service
from src.book_service import find_book_by_title

CHEKHOV = {"name": "Антон Чехов", "country": "Russia", "language": "ru"}


def count(db_path, table):
    with library_service.transaction(db_path) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_add_new_book_creates_new_author(db_path):
    book_id = library_service.add_new_book(
        title="Анна на шее",
        language="ru",
        authors=[CHEKHOV],
        publisher="МИФ",
        db_path=db_path,
    )

    with library_service.transaction(db_path) as connection:
        assert find_book_by_title(connection, "Анна на шее") == book_id

    assert count(db_path, "authors") == 1
    assert count(db_path, "author_names") == 1


def test_add_new_book_with_existing_author(db_path):
    author_id = library_service.add_author(**CHEKHOV, db_path=db_path)

    library_service.add_new_book("Анна на шее", "ru", [{"author_id": author_id}], db_path=db_path)

    assert count(db_path, "authors") == 1
    assert count(db_path, "book_authors") == 1


def test_duplicate_book_is_rejected(db_path):
    author_id = library_service.add_author(**CHEKHOV, db_path=db_path)
    book = dict(title="Анна на шее", language="ru", authors=[{"author_id": author_id}], publisher="МИФ", db_path=db_path)

    library_service.add_new_book(**book)

    with pytest.raises(ValueError):
        library_service.add_new_book(**book)


def test_same_author_in_two_languages_is_one_author(db_path):
    author_id = library_service.add_author(**CHEKHOV, db_path=db_path)
    library_service.add_author_name(author_id, "Anton Chekhov", "en", db_path=db_path)
    author = [{"author_id": author_id}]

    library_service.add_new_book("Анна на шее", "ru", author, publisher="МИФ", db_path=db_path)
    library_service.add_new_book("Anna on the Neck", "en", author, publisher="Penguin", db_path=db_path)

    assert count(db_path, "authors") == 1
    assert count(db_path, "book_authors") == 2


def test_failed_book_does_not_leave_new_author(db_path):
    # The new author is created first; the unknown author_id then fails, so everything is rolled back.
    with pytest.raises(sqlite3.IntegrityError):
        library_service.add_new_book(
            "Анна на шее", "ru", [CHEKHOV, {"author_id": 999}], db_path=db_path
        )

    assert count(db_path, "authors") == 0
    assert count(db_path, "books") == 0
