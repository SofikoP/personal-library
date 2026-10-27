from src.text_utils import normalize


def create_series(connection, series_name):
    cursor = connection.cursor()

    series_name = series_name.strip()

    insert_series = """
        INSERT INTO series (series_name, series_name_normalized)
        VALUES (?, ?)
        """

    cursor.execute(insert_series, (series_name, normalize(series_name)))

    series_id = cursor.lastrowid

    return series_id


def find_series_by_name(connection, series_name):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT series_id
        FROM series
        WHERE series_name_normalized = ?
        """,
        (normalize(series_name),)
    )

    series = cursor.fetchone()

    return None if series is None else series[0]


def get_all_series(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT series_name
        FROM series
        ORDER BY series_name
    """)

    series = cursor.fetchall()

    return [row[0] for row in series]