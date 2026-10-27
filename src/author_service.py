from src.text_utils import normalize


def create_author(connection, country, name, language):
    cursor = connection.cursor()

    insert_author = """
        INSERT INTO authors (country)
        VALUES (?)
        """

    cursor.execute(insert_author, (country,))

    author_id = cursor.lastrowid

    add_author_name(connection, author_id, name, language)

    return author_id


def find_author_by_name(connection, name):
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

    return None if author is None else author[0]


def add_author_name(connection, author_id, name, language):
    cursor = connection.cursor()

    insert_author_name = """
            INSERT INTO author_names (author_id, language, name, name_normalized)
            VALUES (?, ?, ?, ?)
            """

    cursor.execute(insert_author_name, (author_id, language, name, normalize(name)))


def get_all_author_names(connection):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT author_id, name
        FROM author_names
        ORDER BY name
        """
    )

    authors = cursor.fetchall()

    return authors

def get_all_authors(connection):
    """One row per author: (author_id, "name in ru / name in en")."""
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT author_id, GROUP_CONCAT(name, ' / ')
        FROM (SELECT author_id, name FROM author_names ORDER BY language)
        GROUP BY author_id
        ORDER BY 2 COLLATE NOCASE
        """
    )

    return cursor.fetchall()
