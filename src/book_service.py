from src.text_utils import normalize


def add_book(connection, title, language, publisher, series_id=None, volume_number=None):
    cursor = connection.cursor()

    title_normalized = normalize(title)

    query = """
    INSERT INTO books (title, title_normalized, language, publisher, series_id, volume_number)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (title, title_normalized, language, publisher, series_id, volume_number))

    book_id = cursor.lastrowid

    return book_id


def update_book_row(connection, book_id, title, language, publisher, series_id, volume_number):
    """Overwrite the fields stored in the books table (authors and genres are handled separately)."""
    connection.execute(
        """
        UPDATE books
        SET title = ?, title_normalized = ?, language = ?, publisher = ?, series_id = ?, volume_number = ?
        WHERE book_id = ?
        """,
        (title, normalize(title), language, publisher, series_id, volume_number, book_id)
    )


def unlink_book_authors(connection, book_id):
    connection.execute("DELETE FROM book_authors WHERE book_id = ?", (book_id,))


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


def get_book_for_edit(connection, book_id):
    """The book as the edit form needs it: plain fields, author ids and genre names as lists."""
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT b.title, b.language, b.publisher, s.series_name, b.volume_number
        FROM books b
        LEFT JOIN series s ON s.series_id = b.series_id
        WHERE b.book_id = ?
        """,
        (book_id,)
    )

    row = cursor.fetchone()

    if row is None:
        return None

    cursor.execute("SELECT author_id FROM book_authors WHERE book_id = ? ORDER BY author_id", (book_id,))
    author_ids = [author[0] for author in cursor.fetchall()]

    cursor.execute(
        """
        SELECT g.genre_name
        FROM book_genres bg
        JOIN genres g ON g.genre_id = bg.genre_id
        WHERE bg.book_id = ?
        ORDER BY g.genre_name
        """,
        (book_id,)
    )
    genres = [genre[0] for genre in cursor.fetchall()]

    return {
        "book_id": book_id,
        "title": row[0],
        "language": row[1],
        "publisher": row[2],
        "series_name": row[3],
        "volume_number": row[4],
        "author_ids": author_ids,
        "genres": genres,
    }


def find_existing_book(connection, title, language, author_ids, publisher, exclude_book_id=None):
    """Return the id of a book with the same title, language, publisher and authors, or None.

    Title and publisher are compared ignoring case, dots and extra spaces.
    The book exclude_book_id is skipped, so a book being edited is not a duplicate of itself.
    """
    cursor = connection.cursor()

    # Few books share a title, so narrow down in SQL and compare the rest in Python.
    cursor.execute(
        """
        SELECT book_id, publisher
        FROM books
        WHERE title_normalized = ?
        AND language = ?
        """,
        (normalize(title), language)
    )

    for book_id, book_publisher in cursor.fetchall():
        if book_id == exclude_book_id or normalize(book_publisher) != normalize(publisher):
            continue

        cursor.execute(
            """
            SELECT author_id
            FROM book_authors
            WHERE book_id = ?
            """,
            (book_id,)
        )

        if {row[0] for row in cursor.fetchall()} == set(author_ids):
            return book_id

    return None


def get_book_links(connection, book_id):
    """Ids of the authors, genres and series a book is linked to: (author_ids, genre_ids, series_id)."""
    cursor = connection.cursor()

    cursor.execute("SELECT author_id FROM book_authors WHERE book_id = ?", (book_id,))
    author_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT genre_id FROM book_genres WHERE book_id = ?", (book_id,))
    genre_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT series_id FROM books WHERE book_id = ?", (book_id,))
    series_id = cursor.fetchone()[0]

    return author_ids, genre_ids, series_id


def remove_unused(connection, author_ids, genre_ids, series_id):
    """Delete these authors, genres and this series if no book uses them any more."""
    cursor = connection.cursor()

    for author_id in author_ids:
        cursor.execute(
            "DELETE FROM authors WHERE author_id = ? AND author_id NOT IN (SELECT author_id FROM book_authors)",
            (author_id,)
        )

    for genre_id in genre_ids:
        cursor.execute(
            "DELETE FROM genres WHERE genre_id = ? AND genre_id NOT IN (SELECT genre_id FROM book_genres)",
            (genre_id,)
        )

    if series_id is not None:
        cursor.execute(
            """
            DELETE FROM series
            WHERE series_id = ?
            AND series_id NOT IN (SELECT series_id FROM books WHERE series_id IS NOT NULL)
            """,
            (series_id,)
        )


def delete_book(connection, book_id):
    book = get_book(connection, book_id)

    if book is None:
        return None

    author_ids, genre_ids, series_id = get_book_links(connection, book_id)

    connection.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

    remove_unused(connection, author_ids, genre_ids, series_id)

    return book


def get_publishers(connection):
    """Every publisher stored for at least one book, sorted."""
    cursor = connection.cursor()

    cursor.execute("SELECT DISTINCT publisher FROM books")

    return sorted((row[0] for row in cursor.fetchall()), key=str.casefold)


def get_all_books(connection):
    """Rows for the book table: (book_id, title, authors, series, volume, language, publisher).

    Each author is shown by the name in the language of the book; if the author has no name in
    that language, by the name in the first language they have.
    """
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.book_id,
            b.title,
            GROUP_CONCAT(an.name, ', '),
            s.series_name,
            b.volume_number,
            b.language,
            b.publisher
        FROM books b
        LEFT JOIN series s ON s.series_id = b.series_id
        LEFT JOIN book_authors ba ON ba.book_id = b.book_id
        LEFT JOIN author_names an
            ON an.author_id = ba.author_id
            AND an.language = COALESCE(
                (SELECT language FROM author_names WHERE author_id = ba.author_id AND language = b.language),
                (SELECT MIN(language) FROM author_names WHERE author_id = ba.author_id)
            )
        GROUP BY b.book_id
        ORDER BY b.title COLLATE NOCASE
        """
    )

    return cursor.fetchall()
