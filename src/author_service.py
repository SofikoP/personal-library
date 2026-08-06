from src.database import get_connection


def create_author( country, language, name):
        connection = get_connection()
        cursor = connection.cursor()

        insert_author = """
        INSERT INTO authors (country)
        VALUES (?)
        """

        cursor.execute(insert_author, (country,))

        author_id = cursor.lastrowid

        insert_author_name = """
        INSERT INTO author_names (author_id, language, name)
        VALUES (?, ?, ?)
        """

        cursor.execute(insert_author_name, (author_id, language, name))

        connection.commit()
        connection.close()

        return author_id