from database import get_connection



def add_book(title, language, series_id=None, volume_number=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO books (title, language, series_id, volume_number)
    VALUES (?, ?, ?, ?)
    """

    cursor.execute(query, (title, language, series_id, volume_number))

    book_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return book_id

if __name__ == "__main__":
    book_id = add_book(
        title="Harry Potter and the Philosopher's Stone",
        language="en"
    )

    print(book_id)