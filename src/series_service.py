from src.database import get_connection


def create_series(series_name):
    connection = get_connection()
    cursor = connection.cursor()

    insert_series = """
        INSERT INTO series (series_name)
        VALUES (?)
        """

    cursor.execute(insert_series, (series_name,))

    series_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return series_id


def find_series_by_name(series_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT series_id
        FROM series
        WHERE series_name = ?
        """,
        (series_name,)
    )

    series = cursor.fetchone()

    connection.close()

    if series is None:
        return None

    return series[0]


def get_all_series():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT series_name
        FROM series
        ORDER BY series_name
    """)

    series = cursor.fetchall()

    connection.close()

    return [row[0] for row in series]