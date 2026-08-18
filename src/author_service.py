from src.database import get_connection


def create_author(country, name):
    connection = get_connection()
    cursor = connection.cursor()

    insert_author = """
        INSERT INTO authors (country)
        VALUES (?)
        """

    cursor.execute(insert_author, (country,))

    author_id = cursor.lastrowid

    insert_author_name = """
        INSERT INTO author_names (author_id, name)
        VALUES (?, ?)
        """

    cursor.execute(insert_author_name, (author_id, name))

    connection.commit()
    connection.close()

    return author_id


def find_author_by_name(name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
                SELECT author_id
                FROM author_names
                WHERE name = ?
                """,
        (name,)
    )

    author = cursor.fetchone()

    connection.close()

    if author is None:
        return None

    return author[0]


def add_author_name(author_id, name):
    connection = get_connection()
    cursor = connection.cursor()

    insert_author_name = """
            INSERT OR IGNORE INTO author_names (author_id, name)
            VALUES (?, ?)
            """

    cursor.execute(insert_author_name, (author_id, name))

    connection.commit()
    connection.close()


def get_all_author_names():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT author_id, name
        FROM author_names
        ORDER BY name
        """
    )

    authors = cursor.fetchall()

    connection.close()

    return authors