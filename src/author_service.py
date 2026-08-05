from src.database import get_connection


def add_author(country):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO authors (country) VALUES (?)",
        (country,)
    )

    author_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return author_id
