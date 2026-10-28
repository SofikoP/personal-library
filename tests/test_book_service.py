from src import book_service, library_service


def test_add_book(connection):
    book_id = book_service.add_book(connection, title="Dune", language="en", publisher="Ace")

    assert book_service.find_book_by_title(connection, "Dune") == book_id


def test_get_publishers_returns_each_stored_publisher_once(connection):
    book_service.add_book(connection, "A", "en", "Orion")
    book_service.add_book(connection, "B", "en", "Argo")
    book_service.add_book(connection, "C", "en", "Orion")

    assert book_service.get_publishers(connection) == ["Argo", "Orion"]


def test_delete_book(connection):
    book_id = book_service.add_book(connection, title="The Hunger Games", language="en", publisher="Scholastic")

    deleted_book = book_service.delete_book(connection, book_id)

    assert deleted_book is not None
    assert book_service.find_book_by_title(connection, "The Hunger Games") is None


def test_delete_nonexistent_book(connection):
    assert book_service.delete_book(connection, 100500) is None


def test_get_book_for_edit(db_path, connection):
    author_id = library_service.add_author("Антон Чехов", "Russia", "ru", db_path=db_path)
    book_id = library_service.add_new_book(
        "Дюна", "ru", [{"author_id": author_id}], "АСТ",
        genres=["Фантастика", "Роман"], series_name="Сага", volume_number=2, db_path=db_path,
    )

    assert book_service.get_book_for_edit(connection, book_id) == {
        "book_id": book_id,
        "title": "Дюна",
        "language": "ru",
        "publisher": "АСТ",
        "series_name": "Сага",
        "volume_number": 2,
        "author_ids": [author_id],
        "genres": ["Роман", "Фантастика"],
    }


def test_get_book_for_edit_without_series_and_genres(db_path, connection):
    author_id = library_service.add_author("Антон Чехов", "Russia", "ru", db_path=db_path)
    book_id = library_service.add_new_book("Дюна", "ru", [{"author_id": author_id}], "АСТ", db_path=db_path)

    book = book_service.get_book_for_edit(connection, book_id)

    assert book["series_name"] is None
    assert book["volume_number"] is None
    assert book["genres"] == []


def test_get_book_for_edit_nonexistent_book(connection):
    assert book_service.get_book_for_edit(connection, 100500) is None


def test_find_existing_book_can_skip_the_book_being_edited(db_path, connection):
    author_id = library_service.add_author("Антон Чехов", "Russia", "ru", db_path=db_path)
    book_id = library_service.add_new_book("Дюна", "ru", [{"author_id": author_id}], "АСТ", db_path=db_path)

    args = (connection, "Дюна", "ru", [author_id], "АСТ")

    assert book_service.find_existing_book(*args) == book_id
    assert book_service.find_existing_book(*args, exclude_book_id=book_id) is None
