import sqlite3

import pytest

from src import library_service
from src.book_service import find_book_by_title

CHEKHOV = {"name": "Антон Чехов", "country": "Russia", "language": "ru"}


def count(db_path, table):
    with library_service.transaction(db_path) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def add_author(db_path, name="Антон Чехов", language="ru"):
    return {"author_id": library_service.add_author(name, "Russia", language, db_path=db_path)}


def add_book(db_path, authors, title="Анна на шее", language="ru", publisher="МИФ"):
    return library_service.add_new_book(title, language, authors, publisher, db_path=db_path)


# -------------------------
# Adding books and authors
# -------------------------

def test_add_new_book_creates_new_author(db_path):
    book_id = add_book(db_path, [CHEKHOV])

    with library_service.transaction(db_path) as connection:
        assert find_book_by_title(connection, "Анна на шее") == book_id

    assert count(db_path, "authors") == 1
    assert count(db_path, "author_names") == 1


def test_add_new_book_with_existing_author(db_path):
    author = add_author(db_path)

    add_book(db_path, [author])

    assert count(db_path, "authors") == 1
    assert count(db_path, "book_authors") == 1


def test_same_author_in_two_languages_is_one_author(db_path):
    author = add_author(db_path)
    library_service.add_author_name(author["author_id"], "Anton Chekhov", "en", db_path=db_path)

    add_book(db_path, [author])
    add_book(db_path, [author], title="Anna on the Neck", language="en", publisher="Penguin")

    assert count(db_path, "authors") == 1
    assert count(db_path, "book_authors") == 2


def test_failed_book_does_not_leave_new_author(db_path):
    # The new author is created first; the unknown author_id then fails, so everything is rolled back.
    with pytest.raises(sqlite3.IntegrityError):
        add_book(db_path, [CHEKHOV, {"author_id": 999}])

    assert count(db_path, "authors") == 0
    assert count(db_path, "books") == 0


# -------------------------
# Publisher is required
# -------------------------

@pytest.mark.parametrize("publisher", ["", "   ", None])
def test_publisher_is_required(db_path, publisher):
    with pytest.raises(ValueError):
        add_book(db_path, [CHEKHOV], publisher=publisher)

    assert count(db_path, "books") == 0
    assert count(db_path, "authors") == 0


# -------------------------
# Duplicate detection
# -------------------------

def test_duplicate_book_is_rejected(db_path):
    author = add_author(db_path)
    add_book(db_path, [author])

    with pytest.raises(ValueError):
        add_book(db_path, [author])

    assert count(db_path, "books") == 1


def test_duplicate_ignores_case_dots_and_spaces(db_path):
    author = add_author(db_path)
    add_book(db_path, [author], title="Dr. Zhivago", language="en", publisher="Simon & Schuster")

    with pytest.raises(ValueError):
        add_book(db_path, [author], title="  dr  zhivago ", language="en", publisher="SIMON & SCHUSTER")


def test_same_book_in_another_language_is_not_a_duplicate(db_path):
    author = add_author(db_path)
    add_book(db_path, [author], title="Dune", language="en")

    add_book(db_path, [author], title="Dune", language="cs")

    assert count(db_path, "books") == 2


def test_same_book_from_another_publisher_is_not_a_duplicate(db_path):
    author = add_author(db_path)
    add_book(db_path, [author], publisher="МИФ")

    add_book(db_path, [author], publisher="Азбука")

    assert count(db_path, "books") == 2


def test_same_title_with_different_authors_is_not_a_duplicate(db_path):
    first, second = add_author(db_path, "Автор Первый"), add_author(db_path, "Автор Второй")
    add_book(db_path, [first], title="Сборник")

    add_book(db_path, [second], title="Сборник")

    assert count(db_path, "books") == 2


def test_duplicate_is_found_among_several_books_with_the_same_title(db_path):
    # Two books share title, language and publisher; the duplicate is the second one.
    first, second = add_author(db_path, "Автор Первый"), add_author(db_path, "Автор Второй")
    add_book(db_path, [first], title="Сборник")
    add_book(db_path, [second], title="Сборник")

    with pytest.raises(ValueError):
        add_book(db_path, [second], title="Сборник")

    assert count(db_path, "books") == 2


def test_new_author_book_is_not_checked_as_duplicate(db_path):
    add_book(db_path, [CHEKHOV])

    # An author created together with the book cannot already have books, so this is a new book.
    add_book(db_path, [CHEKHOV])

    assert count(db_path, "books") == 2
    assert count(db_path, "authors") == 2


# -------------------------
# A name in another language is saved together with the book
# -------------------------

def author_names(db_path, author_id):
    with library_service.transaction(db_path) as connection:
        rows = connection.execute(
            "SELECT language, name FROM author_names WHERE author_id = ? ORDER BY language", (author_id,)
        ).fetchall()

    return rows


def test_new_author_name_is_saved_with_the_book(db_path):
    author = add_author(db_path)
    add_book(db_path, [author])

    author_with_name = {**author, "name": "Anton Chekhov", "language": "en"}
    add_book(db_path, [author_with_name], title="Anna on the Neck", language="en", publisher="Penguin")

    assert author_names(db_path, author["author_id"]) == [("en", "Anton Chekhov"), ("ru", "Антон Чехов")]


def test_failed_book_does_not_leave_new_author_name(db_path):
    author = add_author(db_path)
    author_with_name = {**author, "name": "Anton Chekhov", "language": "en"}

    # The name is added first; the unknown author_id then fails, so the name is rolled back too.
    with pytest.raises(sqlite3.IntegrityError):
        add_book(db_path, [author_with_name, {"author_id": 999}], title="Anna on the Neck", language="en")

    assert author_names(db_path, author["author_id"]) == [("ru", "Антон Чехов")]
    assert count(db_path, "books") == 0


def test_name_in_a_language_the_author_already_has_is_rejected(db_path):
    author = add_author(db_path)
    author_with_name = {**author, "name": "А. П. Чехов", "language": "ru"}

    with pytest.raises(sqlite3.IntegrityError):
        add_book(db_path, [author_with_name])

    assert count(db_path, "books") == 0
    assert author_names(db_path, author["author_id"]) == [("ru", "Антон Чехов")]


# -------------------------
# Genres can be typed freely
# -------------------------

def genre_names(db_path, book_id):
    with library_service.transaction(db_path) as connection:
        rows = connection.execute(
            """
            SELECT g.genre_name FROM genres g
            JOIN book_genres bg ON bg.genre_id = g.genre_id
            WHERE bg.book_id = ?
            """,
            (book_id,),
        ).fetchall()

    return [row[0] for row in rows]


def test_new_genre_is_created_with_the_book(db_path):
    book_id = library_service.add_new_book(
        "Дюна", "ru", [CHEKHOV], "АСТ", genres=["Фантастика"], db_path=db_path
    )

    assert genre_names(db_path, book_id) == ["Фантастика"]


def test_typed_genre_reuses_existing_genre_ignoring_case(db_path):
    library_service.add_new_book("Дюна", "ru", [CHEKHOV], "АСТ", genres=["Фантастика"], db_path=db_path)

    book_id = library_service.add_new_book(
        "Основание", "ru", [CHEKHOV], "АСТ", genres=["  фантастика "], db_path=db_path
    )

    assert count(db_path, "genres") == 1
    assert genre_names(db_path, book_id) == ["Фантастика"]


def test_same_genre_typed_twice_is_linked_once(db_path):
    book_id = library_service.add_new_book(
        "Дюна", "ru", [CHEKHOV], "АСТ", genres=["Fantasy", "fantasy", ""], db_path=db_path
    )

    assert count(db_path, "genres") == 1
    assert genre_names(db_path, book_id) == ["Fantasy"]


# -------------------------
# Deleting a book cleans up what nothing else uses
# -------------------------

def test_delete_book_removes_unused_author_series_and_genre(db_path):
    book_id = library_service.add_new_book(
        "Дюна", "ru", [CHEKHOV], "АСТ", genres=["Фантастика"], series_name="Сага", db_path=db_path
    )

    library_service.delete_book(book_id, db_path=db_path)

    for table in ("books", "authors", "author_names", "series", "genres"):
        assert count(db_path, table) == 0


def test_delete_book_keeps_author_series_and_genre_used_by_another_book(db_path):
    author = add_author(db_path)
    kwargs = dict(authors=[author], publisher="АСТ", genres=["Фантастика"], series_name="Сага", db_path=db_path)
    first = library_service.add_new_book("Дюна", "ru", **kwargs)
    library_service.add_new_book("Мессия Дюны", "ru", **kwargs)

    library_service.delete_book(first, db_path=db_path)

    assert count(db_path, "books") == 1
    for table in ("authors", "series", "genres"):
        assert count(db_path, table) == 1


# -------------------------
# Editing a book
# -------------------------

from src.book_service import get_book_for_edit


def read_book(db_path, book_id):
    with library_service.transaction(db_path) as connection:
        return get_book_for_edit(connection, book_id)


def test_update_book_fixes_a_typo(db_path):
    author = add_author(db_path)
    book_id = add_book(db_path, [author], title="Анна на шее", publisher="МИФ")

    library_service.update_book(book_id, "Анна на шеe!", "ru", [author], "Азбука", volume_number=3, db_path=db_path)

    book = read_book(db_path, book_id)
    assert (book["title"], book["publisher"], book["volume_number"]) == ("Анна на шеe!", "Азбука", 3)
    assert count(db_path, "books") == 1


def test_update_book_is_not_a_duplicate_of_itself(db_path):
    author = add_author(db_path)
    book_id = add_book(db_path, [author])

    # nothing changes except the volume: the book must not clash with its own old self
    library_service.update_book(book_id, "Анна на шее", "ru", [author], "МИФ", volume_number=2, db_path=db_path)

    assert read_book(db_path, book_id)["volume_number"] == 2


def test_update_book_into_a_duplicate_of_another_book_is_rejected(db_path):
    author = add_author(db_path)
    add_book(db_path, [author], title="Анна на шее")
    other = add_book(db_path, [author], title="Дама с собачкой")

    with pytest.raises(ValueError):
        library_service.update_book(other, "анна на шее", "ru", [author], "миф", db_path=db_path)

    assert read_book(db_path, other)["title"] == "Дама с собачкой"


def test_update_book_removes_the_replaced_author_if_unused(db_path):
    old, new = add_author(db_path, "Автор Старый"), add_author(db_path, "Автор Новый")
    book_id = add_book(db_path, [old])

    library_service.update_book(book_id, "Анна на шее", "ru", [new], "МИФ", db_path=db_path)

    assert read_book(db_path, book_id)["author_ids"] == [new["author_id"]]
    assert count(db_path, "authors") == 1


def test_update_book_keeps_the_replaced_author_if_another_book_uses_it(db_path):
    old, new = add_author(db_path, "Автор Старый"), add_author(db_path, "Автор Новый")
    book_id = add_book(db_path, [old], title="Первая")
    add_book(db_path, [old], title="Вторая")

    library_service.update_book(book_id, "Первая", "ru", [new], "МИФ", db_path=db_path)

    assert count(db_path, "authors") == 2


def test_update_book_replaces_genres_and_series(db_path):
    author = add_author(db_path)
    book_id = library_service.add_new_book(
        "Дюна", "ru", [author], "АСТ", genres=["Фантастка"], series_name="Сага", db_path=db_path
    )

    # fix the typo in the genre and move to another series
    library_service.update_book(
        book_id, "Дюна", "ru", [author], "АСТ", genres=["Фантастика"], series_name="Хроники", db_path=db_path
    )

    book = read_book(db_path, book_id)
    assert (book["genres"], book["series_name"]) == (["Фантастика"], "Хроники")
    assert count(db_path, "genres") == 1   # the misspelled genre is gone
    assert count(db_path, "series") == 1   # the old series is gone


def test_update_book_can_remove_series_and_genres(db_path):
    author = add_author(db_path)
    book_id = library_service.add_new_book(
        "Дюна", "ru", [author], "АСТ", genres=["Фантастика"], series_name="Сага", volume_number=1, db_path=db_path
    )

    library_service.update_book(book_id, "Дюна", "ru", [author], "АСТ", db_path=db_path)

    book = read_book(db_path, book_id)
    assert (book["genres"], book["series_name"], book["volume_number"]) == ([], None, None)
    assert count(db_path, "genres") == 0
    assert count(db_path, "series") == 0


def test_update_book_can_add_an_author_name_in_another_language(db_path):
    author = add_author(db_path)
    book_id = add_book(db_path, [author])

    author_with_name = {**author, "name": "Anton Chekhov", "language": "en"}
    library_service.update_book(book_id, "Анна на шее", "ru", [author_with_name], "МИФ", db_path=db_path)

    assert author_names(db_path, author["author_id"]) == [("en", "Anton Chekhov"), ("ru", "Антон Чехов")]


def test_failed_update_changes_nothing(db_path):
    author = add_author(db_path)
    book_id = library_service.add_new_book(
        "Дюна", "ru", [author], "АСТ", genres=["Фантастика"], series_name="Сага", db_path=db_path
    )
    before = read_book(db_path, book_id)

    # new title, new genre and a new author are all applied first; the unknown author_id then fails
    with pytest.raises(sqlite3.IntegrityError):
        library_service.update_book(
            book_id, "Другое", "ru", [CHEKHOV, {"author_id": 999}], "АСТ",
            genres=["Роман"], series_name="Другая", db_path=db_path,
        )

    assert read_book(db_path, book_id) == before
    assert (count(db_path, "authors"), count(db_path, "genres"), count(db_path, "series")) == (1, 1, 1)


def test_update_book_requires_a_publisher_and_an_existing_book(db_path):
    author = add_author(db_path)
    book_id = add_book(db_path, [author])

    with pytest.raises(ValueError):
        library_service.update_book(book_id, "Анна на шее", "ru", [author], "  ", db_path=db_path)

    with pytest.raises(ValueError):
        library_service.update_book(999, "Анна на шее", "ru", [author], "МИФ", db_path=db_path)


# -------------------------
# Editing an author
# -------------------------

def test_update_author_is_all_or_nothing(db_path):
    author_id = add_author(db_path)["author_id"]
    library_service.add_author_name(author_id, "Anton Chekhov", "en", db_path=db_path)

    # the Russian name is valid and would be saved first, but the English one is empty
    with pytest.raises(ValueError):
        library_service.update_author(author_id, "Russia", {"ru": "А. П. Чехов", "en": " "}, db_path=db_path)

    assert library_service.read_author(author_id, db_path)["names"] == {"en": "Anton Chekhov", "ru": "Антон Чехов"}


def test_updated_author_is_shown_on_all_their_books(db_path):
    author = add_author(db_path, "Антон Чехв")
    add_book(db_path, [author], title="Первая")
    add_book(db_path, [author], title="Вторая")

    library_service.update_author(author["author_id"], "Russia", {"ru": "Антон Чехов"}, db_path=db_path)

    assert {row[2] for row in library_service.list_books(db_path)} == {"Антон Чехов"}


def test_authors_overview_shows_names_country_and_number_of_books(db_path):
    chekhov = add_author(db_path)
    library_service.add_author_name(chekhov["author_id"], "Anton Chekhov", "en", db_path=db_path)
    add_book(db_path, [chekhov], title="Первая")
    add_book(db_path, [chekhov], title="Вторая")
    add_book(db_path, [CHEKHOV], title="Чужая книга")   # a second, different author with one book

    rows = library_service.list_authors_overview(db_path)

    assert [(names, country, books) for _, names, country, books in rows] == [
        ("Anton Chekhov / Антон Чехов", "Russia", 2),
        ("Антон Чехов", "Russia", 1),
    ]


# -------------------------
# The book table shows each author by the name in the book's language
# -------------------------

def authors_column(db_path, title):
    return next(row[2] for row in library_service.list_books(db_path) if row[1] == title)


def test_book_table_shows_the_name_in_the_language_of_the_book(db_path):
    hobb = add_author(db_path, "Робин Хобб", "ru")
    library_service.add_author_name(hobb["author_id"], "Robin Hobb", "en", db_path=db_path)
    add_book(db_path, [hobb], title="Странствия убийцы", language="ru")
    add_book(db_path, [hobb], title="The Wilful Princess", language="en", publisher="HarperCollins")

    assert authors_column(db_path, "Странствия убийцы") == "Робин Хобб"
    assert authors_column(db_path, "The Wilful Princess") == "Robin Hobb"


def test_book_table_falls_back_to_another_name_if_there_is_none_in_the_books_language(db_path):
    weir = add_author(db_path, "Andy Weir", "en")
    add_book(db_path, [weir], title="Marťan", language="cs")

    assert authors_column(db_path, "Marťan") == "Andy Weir"


def test_book_table_lists_several_authors_with_a_comma_and_a_space(db_path):
    first, second = add_author(db_path, "Аркадий Стругацкий"), add_author(db_path, "Борис Стругацкий")
    add_book(db_path, [first, second], title="Пикник на обочине")

    assert sorted(authors_column(db_path, "Пикник на обочине").split(", ")) == ["Аркадий Стругацкий", "Борис Стругацкий"]
