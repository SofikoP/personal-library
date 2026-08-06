from src.author_service import create_author


if __name__ == "__main__":
    author_id = create_author(
        country="UK",
        language="en",
        name="J. K. Rowling"
    )

    print(author_id)