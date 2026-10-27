from src.text_utils import normalize


def add_book(connection, title, language, publisher=None, series_id=None, volume_number=None):
    cursor = connection.cursor()

    title_normalized = normalize(title)

    query = """
    INSERT INTO books (title, title_normalized, language, publisher, series_id, volume_number)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (title, title_normalized, language, publisher, series_id, volume_number))

    book_id = cursor.lastrowid

    return book_id


def find_book_by_title(connection, title):
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

    return None if book is None else book[0]


def link_book_author(connection, book_id, author_id):
    cursor = connection.cursor()

    query = """INSERT INTO book_authors (book_id, author_id)
    VALUES (?, ?)"""

    cursor.execute(query, (book_id, author_id))


def get_book(connection, book_id):
    cursor = connection.cursor()

    query = """
        SELECT
            b.title,
            s.series_name,
            b.volume_number,
            b.language,
            b.publisher,
            GROUP_CONCAT(DISTINCT an.name) AS authors,
            GROUP_CONCAT(DISTINCT g.genre_name) AS genres
        FROM books b
        LEFT JOIN series s
            ON s.series_id = b.series_id
        LEFT JOIN book_authors ba
            ON ba.book_id = b.book_id
        LEFT JOIN author_names an
            ON an.author_id = ba.author_id
        LEFT JOIN book_genres bg
            ON bg.book_id = b.book_id
        LEFT JOIN genres g
            ON g.genre_id = bg.genre_id
        WHERE b.book_id = ?
        GROUP BY b.book_id"""

    cursor.execute(query, (book_id,))

    row = cursor.fetchone()

    if row is None:
        return None

    book = {
        "title": row[0],
        "series_name": row[1],
        "volume_number": row[2],
        "language": row[3],
        "publisher": row[4],
        "authors": row[5],
        "genres": row[6]
    }

    return book


def find_existing_book(connection, title, author_ids, publisher):
    cursor = connection.cursor()

    query = """
    SELECT b.book_id
    FROM books b
    WHERE b.title = ?
    AND b.publisher = ?"""

    cursor.execute(query, (title, publisher))

    book = cursor.fetchone()

    if book is None:
        return None

    book_id = book[0]

    cursor.execute(
        """
        SELECT author_id
        FROM book_authors
        WHERE book_id = ?
        """,
        (book_id,)
    )

    existing_author_ids = {row[0] for row in cursor.fetchall()}

    if set(author_ids) == existing_author_ids:
        return book_id

    return None


def delete_book(connection, book_id):
    cursor = connection.cursor()

    book = get_book(connection, book_id)

    if book is None:
        return None

    cursor.execute(
        """
        SELECT author_id
        FROM book_authors
        WHERE book_id = ?
        """,
        (book_id,))

    author_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT genre_id
        FROM book_genres
        WHERE book_id = ?
        """,
        (book_id,))

    genre_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT
        series_id
        FROM
        books
        WHERE
        book_id = ?
        """,
        (book_id,))

    series_id = cursor.fetchone()[0]

    cursor.execute(
        """
        DELETE FROM books 
        WHERE book_id = ?
        """,
        (book_id,))


    for author_id in author_ids:
        cursor.execute(
            """
            SELECT
            COUNT(*)
            FROM
            book_authors
            WHERE
            author_id = ?
            """,
            (author_id,))

        row = cursor.fetchone()
        book_count = row[0]

        if book_count == 0:
            cursor.execute(
                """
                DELETE FROM authors 
                WHERE author_id = ?
                """,
                (author_id,))

    for genre_id in genre_ids:
        cursor.execute(
            """
            SELECT
            COUNT(*)
            FROM
            book_genres
            WHERE
            genre_id = ?
            """,
            (genre_id,))

        row = cursor.fetchone()
        book_count = row[0]

        if book_count == 0:
            cursor.execute(
                """
                DELETE FROM genres 
                WHERE genre_id = ?
                """,
                (genre_id,))

    if series_id is not None:
        cursor.execute(
            """
            SELECT
            COUNT(*)
            FROM
            books
            WHERE
            series_id = ?
            """,
            (series_id,))

        row = cursor.fetchone()
        book_count = row[0]

        if book_count == 0:
            cursor.execute(
                """
                DELETE FROM series 
                WHERE series_id = ?
                """,
                (series_id,))


    return book



def get_all_books(connection):
    """Rows for the book table: (book_id, title, authors, series, volume, language, publisher)."""
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.book_id,
            b.title,
            GROUP_CONCAT(DISTINCT an.name),
            s.series_name,
            b.volume_number,
            b.language,
            b.publisher
        FROM books b
        LEFT JOIN series s ON s.series_id = b.series_id
        LEFT JOIN book_authors ba ON ba.book_id = b.book_id
        LEFT JOIN author_names an ON an.author_id = ba.author_id
        GROUP BY b.book_id
        ORDER BY b.title COLLATE NOCASE
        """
    )

    return cursor.fetchall()
