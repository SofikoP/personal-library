def create_genre(connection, genre_name):
    cursor = connection.cursor()

    insert_genre = """
            INSERT INTO genres (genre_name)
            VALUES (?)
            """

    cursor.execute(insert_genre, (genre_name,))

    genre_id = cursor.lastrowid

    return genre_id


def link_book_genre(connection, book_id, genre_id):
    cursor = connection.cursor()

    query = """INSERT INTO book_genres (book_id, genre_id)
    VALUES (?, ?)"""

    cursor.execute(query, (book_id, genre_id))


def find_genre_by_name(connection, name):
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

    return None if genre is None else genre[0]


def get_all_genres(connection):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT genre_name
        FROM genres
        ORDER BY genre_name
        """
    )

    genres = cursor.fetchall()

    return [genre[0] for genre in genres]