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


def test_get_countries_returns_each_stored_country_once(connection):
    author_service.create_author(connection, "Sweden", "Fredrik Backman", "en")
    author_service.create_author(connection, "England", "Terry Pratchett", "en")
    author_service.create_author(connection, "Sweden", "Astrid Lindgren", "en")

    assert author_service.get_countries(connection) == ["England", "Sweden"]


# -------------------------
# Editing an author
# -------------------------

def names_of(connection, author_id):
    return author_service.get_author_for_edit(connection, author_id)["names"]


def test_get_author_for_edit(connection):
    author_id = author_service.create_author(connection, "Russia", "Антон Чехов", "ru")
    author_service.add_author_name(connection, author_id, "Anton Chekhov", "en")

    assert author_service.get_author_for_edit(connection, author_id) == {
        "author_id": author_id,
        "country": "Russia",
        "names": {"en": "Anton Chekhov", "ru": "Антон Чехов"},
    }
    assert author_service.get_author_for_edit(connection, 100500) is None


def test_update_author_fixes_a_typo_and_the_country(connection):
    author_id = author_service.create_author(connection, "Rusia", "Антон Чехв", "ru")

    author_service.update_author(connection, author_id, "Russia", {"ru": "Антон Чехов"})

    assert author_service.get_author_for_edit(connection, author_id)["country"] == "Russia"
    assert names_of(connection, author_id) == {"ru": "Антон Чехов"}


def test_update_author_updates_the_search_text_too(connection):
    author_id = author_service.create_author(connection, "Russia", "Антон Чехв", "ru")

    author_service.update_author(connection, author_id, "Russia", {"ru": "А. П. Чехов"})

    stored = connection.execute("SELECT name_normalized FROM author_names WHERE author_id = ?", (author_id,)).fetchone()
    assert stored[0] == "а п чехов"


def test_update_author_changes_only_the_given_names(connection):
    author_id = author_service.create_author(connection, "Russia", "Антон Чехов", "ru")
    author_service.add_author_name(connection, author_id, "Anton Chekhv", "en")

    author_service.update_author(connection, author_id, "Russia", {"en": "Anton Chekhov"})

    assert names_of(connection, author_id) == {"en": "Anton Chekhov", "ru": "Антон Чехов"}


def test_update_author_rejects_a_name_taken_by_another_author(connection):
    author_service.create_author(connection, "Russia", "Антон Чехов", "ru")
    typo = author_service.create_author(connection, "Russia", "Антон Чехв", "ru")

    with pytest.raises(ValueError):
        author_service.update_author(connection, typo, "Russia", {"ru": "  антон  ЧЕХОВ "})

    assert names_of(connection, typo) == {"ru": "Антон Чехв"}


def test_update_author_allows_the_same_text_in_two_languages_of_one_author(connection):
    author_id = author_service.create_author(connection, "Czech Republic", "Karel Čapek", "cs")
    author_service.add_author_name(connection, author_id, "Karel Čapek", "en")

    author_service.update_author(connection, author_id, "Czech Republic", {"en": "Karel Čapek"})


@pytest.mark.parametrize("country, names", [
    ("", {"ru": "Антон Чехов"}),             # country is required
    ("Russia", {"ru": "   "}),                # a name cannot be empty
    ("Russia", {"en": "Anton Chekhov"}),      # a new language cannot be added here
])
def test_update_author_rejects_bad_input_and_changes_nothing(connection, country, names):
    author_id = author_service.create_author(connection, "Russia", "Антон Чехов", "ru")

    with pytest.raises(ValueError):
        author_service.update_author(connection, author_id, country, names)

    assert author_service.get_author_for_edit(connection, author_id) == {
        "author_id": author_id, "country": "Russia", "names": {"ru": "Антон Чехов"},
    }


def test_update_unknown_author(connection):
    with pytest.raises(ValueError):
        author_service.update_author(connection, 100500, "Russia", {})
