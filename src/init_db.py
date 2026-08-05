import sqlite3


connection = sqlite3.connect("data/library.db")

with open("sql/create_tables.sql", "r", encoding="utf-8") as file:
    sql_script = file.read()

connection.executescript(sql_script)
connection.commit()
connection.close()