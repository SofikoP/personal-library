from src.book_service import add_book, link_book_author, find_existing_book
from src.author_service import create_author, find_author_by_name
from src.series_service import create_series, find_series_by_name
from src.genre_service import create_genre, find_genre_by_name, link_book_genre



def add_new_book(title, language, authors, genres=None, publisher=None, series_name=None, volume_number=None):
    existing_book_id = find_existing_book(title, authors, publisher)

    if existing_book_id is not None:
        raise ValueError("Book already exists.")

    series_id = None

    if series_name is not None:
        series_id = find_series_by_name(series_name)

        if series_id is None:
            series_id = create_series(series_name)

    book_id = add_book(title, language, publisher, series_id, volume_number)

    for author in authors:
        author_id = find_author_by_name(author["name"])

        if author_id is None:
            author_id = create_author(author["country"], author["name"])

        link_book_author(book_id, author_id)

    if genres is not None:
        for genre in genres:
            genre_id = find_genre_by_name(genre)

            if genre_id is None:
                genre_id = create_genre(genre)

            link_book_genre(book_id, genre_id)

    return book_id