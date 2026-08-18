from src.database import get_connection


def create_genre(genre_name):
    connection = get_connection()
    cursor = connection.cursor()

    insert_genre = """
            INSERT OR IGNORE INTO genres (genre_name)
            VALUES (?)
            """

    cursor.execute(insert_genre, (genre_name,))

    genre_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return genre_id


def link_book_genre(book_id, genre_id):
    connection = get_connection()
    cursor = connection.cursor()

    query = """INSERT INTO book_genres (book_id, genre_id)
    VALUES (?, ?)"""

    cursor.execute(query, (book_id, genre_id))

    connection.commit()
    connection.close()


def find_genre_by_name(name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT genre_id
        FROM genres
        WHERE genre_name = ?
        """,
        (name,)
    )

    genre = cursor.fetchone()

    connection.close()

    if genre is None:
        return None

    return genre[0]


def get_all_genres():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT genre_name
        FROM genres
        ORDER BY genre_name
        """
    )

    genres = cursor.fetchall()

    connection.close()

    return [genre[0] for genre in genres]