import sqlite3


def get_connection():
    connection = sqlite3.connect("data/library.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection