from src.database import transaction, DB_PATH
from src.book_service import (
    add_book, link_book_author, find_existing_book, get_all_books, get_publishers, get_book, get_book_for_edit, get_book_links,
    remove_unused, unlink_book_authors, update_book_row, delete_book as delete_book_from_db,
)
from src.author_service import (
    create_author, get_all_authors, get_author_for_edit, get_authors_overview, add_author_name as add_author_name_to_db,
    update_author as update_author_in_db, get_countries,
)
from src.series_service import create_series, find_series_by_name, get_all_series
from src.genre_service import create_genre, find_genre_by_name, link_book_genre, unlink_book_genres, get_all_genres


def add_author(name, country, language, db_path=DB_PATH):
    with transaction(db_path) as connection:
        return create_author(connection, country, name, language)


def add_author_name(author_id, name, language, db_path=DB_PATH):
    with transaction(db_path) as connection:
        add_author_name_to_db(connection, author_id, name, language)


def clean_publisher(publisher):
    publisher = (publisher or "").strip()

    if not publisher:
        raise ValueError("Publisher is required.")

    return publisher


def check_not_duplicate(connection, title, language, authors, publisher, exclude_book_id=None):
    # A book with a brand-new author cannot be a duplicate, so check only when all authors exist.
    if not all("author_id" in author for author in authors):
        return

    author_ids = [author["author_id"] for author in authors]

    if find_existing_book(connection, title, language, author_ids, publisher, exclude_book_id) is not None:
        raise ValueError("Book already exists.")


def find_or_create_series(connection, series_name):
    """Id of the series with this name (created if needed), or None if there is no series."""
    if not series_name or not series_name.strip():
        return None

    series_id = find_series_by_name(connection, series_name)

    if series_id is None:
        series_id = create_series(connection, series_name)

    return series_id


def link_authors(connection, book_id, authors):
    for author in authors:
        if "author_id" in author:
            author_id = author["author_id"]

            if "name" in author:
                add_author_name_to_db(connection, author_id, author["name"], author["language"])
        else:
            author_id = create_author(connection, author["country"], author["name"], author["language"])

        link_book_author(connection, book_id, author_id)


def link_genres(connection, book_id, genres):
    linked_genre_ids = set()

    for genre in genres or []:
        genre = genre.strip()

        if not genre:
            continue

        genre_id = find_genre_by_name(connection, genre)

        if genre_id is None:
            genre_id = create_genre(connection, genre)

        # "fantasy" and "Fantasy" typed together are one genre: link it once
        if genre_id not in linked_genre_ids:
            link_book_genre(connection, book_id, genre_id)
            linked_genre_ids.add(genre_id)


def add_new_book(title, language, authors, publisher, genres=None, series_name=None, volume_number=None, db_path=DB_PATH):
    """Add a book. Each author is one of:

    {"author_id": 1}                                  an existing author
    {"author_id": 1, "name": "...", "language": "en"} an existing author plus a name in another language
    {"name": "...", "country": "...", "language": ""} a new author

    Everything is saved in one transaction together with the book.
    """
    publisher = clean_publisher(publisher)

    with transaction(db_path) as connection:
        check_not_duplicate(connection, title, language, authors, publisher)

        series_id = find_or_create_series(connection, series_name)
        book_id = add_book(connection, title, language, publisher, series_id, volume_number)

        link_authors(connection, book_id, authors)
        link_genres(connection, book_id, genres)

        return book_id


def update_book(book_id, title, language, authors, publisher, genres=None, series_name=None, volume_number=None, db_path=DB_PATH):
    """Replace everything about a book; authors have the same format as in add_new_book.

    Authors, genres and the series that no book uses after the change are removed.
    Everything is saved in one transaction.
    """
    publisher = clean_publisher(publisher)

    with transaction(db_path) as connection:
        if get_book(connection, book_id) is None:
            raise ValueError("Book not found.")

        old_author_ids, old_genre_ids, old_series_id = get_book_links(connection, book_id)

        check_not_duplicate(connection, title, language, authors, publisher, exclude_book_id=book_id)

        series_id = find_or_create_series(connection, series_name)
        update_book_row(connection, book_id, title, language, publisher, series_id, volume_number)

        unlink_book_authors(connection, book_id)
        unlink_book_genres(connection, book_id)
        link_authors(connection, book_id, authors)
        link_genres(connection, book_id, genres)

        remove_unused(connection, old_author_ids, old_genre_ids, old_series_id)


def delete_book(book_id, db_path=DB_PATH):
    with transaction(db_path) as connection:
        return delete_book_from_db(connection, book_id)


def read_author(author_id, db_path=DB_PATH):
    """The author as the edit form needs it (see author_service.get_author_for_edit), or None."""
    with transaction(db_path) as connection:
        return get_author_for_edit(connection, author_id)


def update_author(author_id, country, names, db_path=DB_PATH):
    """Change an author's country and names ({language: new name}); all or nothing."""
    with transaction(db_path) as connection:
        update_author_in_db(connection, author_id, country, names)


def read_book(book_id, db_path=DB_PATH):
    """The book as the edit form needs it (see book_service.get_book_for_edit), or None."""
    with transaction(db_path) as connection:
        return get_book_for_edit(connection, book_id)


def list_authors(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_authors(connection)


def list_authors_overview(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_authors_overview(connection)


def list_countries(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_countries(connection)


def list_publishers(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_publishers(connection)


def list_series(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_series(connection)


def list_genres(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_genres(connection)


def list_books(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_books(connection)
