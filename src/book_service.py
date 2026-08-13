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
        connection.close()
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

    connection.close()

    return book


def find_existing_book(title, authors, publisher):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT b.book_id
    FROM books b
    WHERE b.title = ?
    AND b.publisher = ?"""

    cursor.execute(query, (title, publisher))

    book = cursor.fetchone()

    if book is None:
        connection.close()
        return None

    book_id = book[0]

    cursor.execute(
        """
        SELECT an.name
        FROM author_names an
        INNER JOIN book_authors ba
            ON an.author_id = ba.author_id
        WHERE ba.book_id = ?
        """,
        (book_id,)
    )

    existing_authors = cursor.fetchall()

    existing_author_names = []

    for author in existing_authors:
        existing_author_names.append(author[0])

    author_names = []

    for author in authors:
        author_names.append(author["name"])

    connection.close()

    if set(author_names) == set(existing_author_names):
        return book_id

    return None

if __name__ == "__main__":
    print(find_existing_book("My Friends", [{"name": "Fredrik Backman"}], "Simon & Schuster"))
    print(get_book(2))