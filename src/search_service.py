from src.database import get_connection


def search_books_by_title(title):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            book_id,
            title
        FROM books
        WHERE title LIKE ?
        """

    cursor.execute(query, (f"%{title}%",))

    rows = [{"book_id": row[0], "title": row[1]} for row in cursor.fetchall()]

    connection.close()

    return rows


def search_books_by_author(author):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT DISTINCT
            b.book_id,
            b.title
        FROM books b
        INNER JOIN book_authors ba
        ON b.book_id = ba.book_id
        INNER JOIN author_names an
        ON ba.author_id = an.author_id
        WHERE an.name LIKE ?
        """

    cursor.execute(query, (f"%{author}%",))

    rows = [{"book_id": row[0], "title": row[1]} for row in cursor.fetchall()]

    connection.close()

    return rows


def search_books_by_series(series):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT DISTINCT
            b.book_id,
            b.title
        FROM books b
        INNER JOIN series s
        ON b.series_id = s.series_id
        WHERE s.series_name LIKE ?
        """

    cursor.execute(query, (f"%{series}%",))

    rows = [{"book_id": row[0], "title": row[1]} for row in cursor.fetchall()]

    connection.close()

    return rows

def search_books(query):
    title_books = search_books_by_title(query)
    author_books = search_books_by_author(query)
    series_books = search_books_by_series(query)

    all_books = title_books + author_books + series_books
    result = []

    for book in all_books:
        if book not in result:
         result.append(book)

    return result