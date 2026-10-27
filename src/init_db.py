from pathlib import Path
from src.database import get_connection, DB_PATH, SQL_PATH


def initialize_database(path=DB_PATH):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection(path)

    with open(SQL_PATH, "r", encoding="utf-8") as file:
        sql_script = file.read()

    connection.executescript(sql_script)
    connection.commit()
    connection.close()