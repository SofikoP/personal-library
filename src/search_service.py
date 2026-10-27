from src.text_utils import normalize


def search_books_by_title(connection, query):
    normalized_query = normalize(query)

    if not normalized_query:
        return []

    cursor = connection.cursor()

    query_sql = """
        SELECT book_id, title
        FROM books
        WHERE title_normalized LIKE ?
    """

    cursor.execute(query_sql, (f"%{normalized_query}%",))

    rows = [{"book_id": row[0], "title": row[1]} for row in cursor.fetchall()]

    return rows


def search_books_by_author(connection, query):
    normalized_query = normalize(query)

    if not normalized_query:
        return []

    cursor = connection.cursor()

    query_sql = """
        SELECT DISTINCT
            b.book_id,
            b.title
        FROM books b
        INNER JOIN book_authors ba
            ON b.book_id = ba.book_id
        INNER JOIN author_names an
            ON ba.author_id = an.author_id
        WHERE an.name_normalized LIKE ?
        """

    cursor.execute(query_sql, (f"%{normalized_query}%",))

    rows = [{"book_id": row[0], "title": row[1]} for row in cursor.fetchall()]

    return rows

def search_books_by_series(connection, query):
    normalized_query = normalize(query)

    if not normalized_query:
        return []

    cursor = connection.cursor()

    query_sql = """
        SELECT DISTINCT
            b.book_id,
            b.title
        FROM books b
        INNER JOIN series s
            ON b.series_id = s.series_id
        WHERE s.series_name_normalized LIKE ?
        """

    cursor.execute(query_sql, (f"%{normalized_query}%",))

    rows = [{"book_id": row[0], "title": row[1]} for row in cursor.fetchall()]

    return rows

def search_books(connection, query):
    title_books = search_books_by_title(connection,query)
    author_books = search_books_by_author(connection, query)
    series_books = search_books_by_series(connection, query)

    all_books = title_books + author_books + series_books
    result = []

    for book in all_books:
        if book not in result:
            result.append(book)

    return result