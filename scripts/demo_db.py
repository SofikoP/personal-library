from pathlib import Path

from src.database import PROJECT_ROOT
from src.init_db import initialize_database
from src.library_service import add_author, add_author_name, add_new_book

DEMO_DB_PATH = PROJECT_ROOT / "data" / "demo.db"


def create_demo_database(path=DEMO_DB_PATH):
    """Create a small sample database. Does nothing if the file already exists."""
    path = Path(path)

    if path.exists():
        return path

    initialize_database(path)

    # One author with names in two languages, so the same author has books in ru and en.
    backman = add_author("Фредерик Бакман", "Sweden", "ru", db_path=path)
    add_author_name(backman, "Fredrik Backman", "en", db_path=path)

    add_new_book("Тревожные люди", "ru", [{"author_id": backman}],
                 genres=["Роман"], publisher="Синдбад", db_path=path)
    add_new_book("My Friends", "en", [{"author_id": backman}],
                 genres=["Novel"], publisher="Simon & Schuster", db_path=path)

    # New authors are created together with their books.
    add_new_book("Marťan", "cs",
                 [{"name": "Andy Weir", "country": "United States", "language": "en"}],
                 genres=["Science Fiction"], publisher="Laser", db_path=path)
    add_new_book("Гарри Поттер и философский камень", "ru",
                 [{"name": "Джоан Роулинг", "country": "United Kingdom", "language": "ru"}],
                 genres=["Fantasy"], series_name="Гарри Поттер", volume_number=1,
                 publisher="Росмэн", db_path=path)

    return path
