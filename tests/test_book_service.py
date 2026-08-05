from src.book_service import add_book, find_book_by_title


if __name__ == "__main__":
    book_id = add_book(
        title="Dune",
        language="en"
    )

    assert find_book_by_title("Dune") == book_id

    print("Test passed")