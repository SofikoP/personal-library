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


def get_all_authors(connection):
    """One row per author: (author_id, "name in en / name in ru", "en,ru")."""
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT author_id, GROUP_CONCAT(name, ' / '), GROUP_CONCAT(language)
        FROM (SELECT author_id, name, language FROM author_names ORDER BY language)
        GROUP BY author_id
        ORDER BY 2 COLLATE NOCASE
        """
    )

    return cursor.fetchall()


def get_author_for_edit(connection, author_id):
    """The author as the edit form needs it: {"author_id", "country", "names": {language: name}}, or None."""
    cursor = connection.cursor()

    cursor.execute("SELECT country FROM authors WHERE author_id = ?", (author_id,))
    row = cursor.fetchone()

    if row is None:
        return None

    cursor.execute("SELECT language, name FROM author_names WHERE author_id = ? ORDER BY language", (author_id,))

    return {"author_id": author_id, "country": row[0], "names": dict(cursor.fetchall())}


def update_author(connection, author_id, country, names):
    """Change the country and the text of the author's names; names is {language: new name}.

    Languages cannot be added or changed here, and a name may not be taken by another author.
    """
    author = get_author_for_edit(connection, author_id)

    if author is None:
        raise ValueError("Author not found.")

    country = (country or "").strip()

    if not country:
        raise ValueError("Country is required.")

    cursor = connection.cursor()

    for language, name in names.items():
        name = (name or "").strip()

        if language not in author["names"]:
            raise ValueError(f"The author has no name in language '{language}'.")

        if not name:
            raise ValueError("A name cannot be empty.")

        cursor.execute(
            "SELECT 1 FROM author_names WHERE name_normalized = ? AND author_id != ?",
            (normalize(name), author_id)
        )

        if cursor.fetchone() is not None:
            raise ValueError("Another author already has this name.")

        cursor.execute(
            "UPDATE author_names SET name = ?, name_normalized = ? WHERE author_id = ? AND language = ?",
            (name, normalize(name), author_id, language)
        )

    cursor.execute("UPDATE authors SET country = ? WHERE author_id = ?", (country, author_id))


def get_countries(connection):
    """Every country that is stored for at least one author, sorted."""
    cursor = connection.cursor()

    cursor.execute("SELECT DISTINCT country FROM authors WHERE country IS NOT NULL AND country != ''")

    return sorted((row[0] for row in cursor.fetchall()), key=str.casefold)


def get_authors_overview(connection):
    """Rows for the author table: (author_id, "name / name", country, number of books)."""
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            a.author_id,
            (SELECT GROUP_CONCAT(name, ' / ')
             FROM (SELECT name FROM author_names WHERE author_id = a.author_id ORDER BY language)),
            a.country,
            (SELECT COUNT(*) FROM book_authors WHERE author_id = a.author_id)
        FROM authors a
        ORDER BY 2 COLLATE NOCASE
        """
    )

    return cursor.fetchall()
