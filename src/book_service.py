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


def get_book(book_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            b.title,
            b.language,
            b.publisher,
            s.series_name,
            b.volume_number,
            an.name
        FROM books b
        LEFT JOIN series s
            ON b.series_id = s.series_id
        INNER JOIN book_authors ba
            ON b.book_id = ba.book_id
        INNER JOIN author_names an
            ON ba.author_id = an.author_id
        WHERE b.book_id = ?"""

    cursor.execute(query, (book_id,))

    rows = cursor.fetchall()

    if not rows:
        connection.close()
        return None

    authors = []

    for row in rows:
        authors.append(row[5])

    book = {
        "title": rows[0][0],
        "language": rows[0][1],
        "publisher": rows[0][2],
        "series_name": rows[0][3],
        "volume_number": rows[0][4],
        "authors": authors
            }

    connection.close()

    return book