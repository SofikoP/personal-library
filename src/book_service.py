from src.database import get_connection


def add_book(title, language, publisher=None, series_id=None, volume_number=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO books (title, language, publisher, series_id, volume_number)
    VALUES (?, ?, ?, ?, ?)
    """

    cursor.execute(query, (title, language, publisher, series_id, volume_number))

    book_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return book_id


def find_book_by_title(title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT book_id
        FROM books
        WHERE title = ?
        """,
        (title,)
    )

    book = cursor.fetchone()

    connection.close()

    if book is None:
        return None

    return book[0]


def link_book_author(book_id, author_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = """INSERT INTO book_authors (book_id, author_id)
    VALUES (?, ?)"""

    cursor.execute(query, (book_id, author_id))

    connection.commit()
    connection.close()