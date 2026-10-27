from src.database import transaction, DB_PATH
from src.book_service import add_book, link_book_author, find_existing_book, get_all_books, delete_book as delete_book_from_db
from src.author_service import create_author, get_all_authors, add_author_name as add_author_name_to_db
from src.series_service import create_series, find_series_by_name, get_all_series
from src.genre_service import create_genre, find_genre_by_name, link_book_genre, get_all_genres


def add_author(name, country, language, db_path=DB_PATH):
    with transaction(db_path) as connection:
        return create_author(connection, country, name, language)


def add_author_name(author_id, name, language, db_path=DB_PATH):
    with transaction(db_path) as connection:
        add_author_name_to_db(connection, author_id, name, language)


def add_new_book(title, language, authors, genres=None, publisher=None, series_name=None, volume_number=None, db_path=DB_PATH):
    """Each author is either {"author_id": 1} (existing) or {"name", "country", "language"} (new)."""
    with transaction(db_path) as connection:
        # A book with a brand-new author cannot be a duplicate, so check only when all authors exist.
        if all("author_id" in author for author in authors):
            author_ids = [author["author_id"] for author in authors]
            existing_book_id = find_existing_book(connection, title, author_ids, publisher)

            if existing_book_id is not None:
                raise ValueError("Book already exists.")

        series_id = None

        if series_name is not None:
            series_id = find_series_by_name(connection, series_name)

            if series_id is None:
                series_id = create_series(connection, series_name)

        book_id = add_book(connection, title, language, publisher, series_id, volume_number)

        for author in authors:
            if "author_id" in author:
                author_id = author["author_id"]
            else:
                author_id = create_author(connection, author["country"], author["name"], author["language"])

            link_book_author(connection, book_id, author_id)

        for genre in genres or []:
            genre_id = find_genre_by_name(connection, genre)

            if genre_id is None:
                genre_id = create_genre(connection, genre)

            link_book_genre(connection, book_id, genre_id)

        return book_id


def delete_book(book_id, db_path=DB_PATH):
    with transaction(db_path) as connection:
        return delete_book_from_db(connection, book_id)


def list_authors(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_authors(connection)


def list_series(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_series(connection)


def list_genres(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_genres(connection)


def list_books(db_path=DB_PATH):
    with transaction(db_path) as connection:
        return get_all_books(connection)
