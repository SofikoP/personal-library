from src import book_service


def test_add_book(connection):
    book_id = book_service.add_book(connection, title="Dune", language="en")

    assert book_service.find_book_by_title(connection, "Dune") == book_id


def test_delete_book(connection):
    book_id = book_service.add_book(connection, title="The Hunger Games", language="en")

    deleted_book = book_service.delete_book(connection, book_id)

    assert deleted_book is not None
    assert book_service.find_book_by_title(connection, "The Hunger Games") is None


def test_delete_nonexistent_book(connection):
    assert book_service.delete_book(connection, 100500) is None