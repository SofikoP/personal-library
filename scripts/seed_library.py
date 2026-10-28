"""Create a new library database and fill it with the starting set of books.

    python -m scripts.seed_library              creates data/library.db
    python -m scripts.seed_library some.db      creates some.db instead

It never touches an existing file: if the database already exists it stops with a message.
"""
import sys
from pathlib import Path

from src.database import DB_PATH, transaction
from src.genre_service import create_genre
from src.init_db import initialize_database
from src.library_service import add_author, add_author_name, add_new_book

# Each author once: key -> (country, {language of the name: name}). The first name is created with the author.
AUTHORS = {
    "backman": ("Sweden", {"ru": "Фредерик Бакман", "en": "Fredrik Backman"}),
    "weir": ("United States", {"cs": "Andy Weir"}),
    "sanderson": ("United States", {"ru": "Брендон Сандерсон"}),
    "hobb": ("United States", {"ru": "Робин Хобб", "en": "Robin Hobb"}),
    "tartt": ("United States", {"ru": "Донна Тартт"}),
    "atwood": ("Canada", {"cs": "Margaret Atwood"}),
    "cronin": ("Scotland", {"ru": "Арчибальд Кронин"}),
    "corey": ("United States", {"ru": "Джеймс Кори"}),
    "collins": ("United States", {"en": "Suzanne Collins"}),
    "arkady": ("Russia", {"ru": "Аркадий Стругацкий"}),
    "boris": ("Russia", {"ru": "Борис Стругацкий"}),
    "patterson": ("United States", {"cs": "James Patterson"}),
}

# Genres that exist from the start, so they can be picked from the list.
GENRES = [
    "Classic Literature",
    "Dystopian Fiction",
    "Fantasy",
    "Historical Fiction",
    "Literary Fiction",
    "Modern Prose",
    "Mystery",
    "Romance",
    "Science Fiction",
    "Thriller",
    "Young Adult",
]

# "authors" lists keys of AUTHORS.
BOOKS = [
    {"title": "Тревожные люди", "language": "ru", "authors": ["backman"], "publisher": "Синдбад"},
    {"title": "My Friends", "language": "en", "authors": ["backman"], "publisher": "Simon & Schuster"},
    {"title": "Marťan", "language": "cs", "authors": ["weir"], "publisher": "Laser",
     "genres": ["Science Fiction"]},
    {"title": "Элантрис", "language": "ru", "authors": ["sanderson"], "publisher": "Азбука",
     "genres": ["Fantasy"]},
    {"title": "Локон с изумрудного моря", "language": "ru", "authors": ["sanderson"], "publisher": "Азбука"},
    {"title": "Озаренный Солнцем", "language": "ru", "authors": ["sanderson"], "publisher": "Азбука"},
    {"title": "Юми и укротитель кошмаров", "language": "ru", "authors": ["sanderson"], "publisher": "Азбука"},
    {"title": "Ученик убийцы. Королевский убийца", "language": "ru", "authors": ["hobb"], "publisher": "Азбука",
     "genres": ["Fantasy"], "series_name": "Сага о Видящих", "volume_number": 1},
    {"title": "Странствия убийцы", "language": "ru", "authors": ["hobb"], "publisher": "Азбука",
     "genres": ["Fantasy"], "series_name": "Сага о Видящих", "volume_number": 2},
    {"title": "The Wilful Princess and the Piebald Prince", "language": "en", "authors": ["hobb"],
     "publisher": "HarperCollins"},
    {"title": "Тайная история", "language": "ru", "authors": ["tartt"], "publisher": "Corpus",
     "genres": ["Modern Prose", "Literary Fiction"]},
    {"title": "Alias Grace", "language": "cs", "authors": ["atwood"], "publisher": "Argo",
     "genres": ["Historical Fiction", "Literary Fiction"]},
    {"title": "Příběh služebnice", "language": "cs", "authors": ["atwood"], "publisher": "Argo"},
    {"title": "Svědectví", "language": "cs", "authors": ["atwood"], "publisher": "Argo"},
    {"title": "Замок Броуди", "language": "ru", "authors": ["cronin"], "publisher": "Иностранка",
     "genres": ["Classic Literature"]},
    {"title": "Пробуждение Левиафана", "language": "ru", "authors": ["corey"], "publisher": "Азбука",
     "genres": ["Science Fiction"], "series_name": "Пространство", "volume_number": 1},
    {"title": "Война Калибана", "language": "ru", "authors": ["corey"], "publisher": "Азбука",
     "genres": ["Science Fiction"], "series_name": "Пространство", "volume_number": 2},
    {"title": "Врата Абаддона", "language": "ru", "authors": ["corey"], "publisher": "Азбука",
     "genres": ["Science Fiction"], "series_name": "Пространство", "volume_number": 3},
    {"title": "The Hunger Games", "language": "en", "authors": ["collins"], "publisher": "Scholastic",
     "series_name": "The Hunger Games", "volume_number": 1},
    {"title": "Catching Fire", "language": "en", "authors": ["collins"], "publisher": "Scholastic",
     "series_name": "The Hunger Games", "volume_number": 2},
    {"title": "Mockingjay", "language": "en", "authors": ["collins"], "publisher": "Scholastic",
     "series_name": "The Hunger Games", "volume_number": 3},
    {"title": "The Ballad of Songbirds and Snakes", "language": "en", "authors": ["collins"],
     "publisher": "Scholastic", "series_name": "The Hunger Games"},
    {"title": "Град обреченный", "language": "ru", "authors": ["arkady", "boris"], "publisher": "АСТ",
     "genres": ["Science Fiction", "Dystopian Fiction"]},
    {"title": "Пикник на обочине", "language": "ru", "authors": ["arkady", "boris"], "publisher": "АСТ"},
]


def seed(path):
    """Create the database at path (it must not exist yet) and fill it."""
    initialize_database(path)

    with transaction(path) as connection:
        for genre in GENRES:
            create_genre(connection, genre)

    author_ids = {}

    for key, (country, names) in AUTHORS.items():
        (language, name), *other_names = names.items()
        author_ids[key] = add_author(name, country, language, db_path=path)

        for language, name in other_names:
            add_author_name(author_ids[key], name, language, db_path=path)

    for book in BOOKS:
        authors = [{"author_id": author_ids[key]} for key in book["authors"]]
        add_new_book(**{**book, "authors": authors}, db_path=path)


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DB_PATH

    if path.exists():
        print(f"{path} already exists, nothing was changed.")
        print("Move or rename the old file first if you want a fresh database.")
        sys.exit(1)

    try:
        seed(path)
    except Exception:
        path.unlink(missing_ok=True)  # the file was created by this run, so a half-filled one is removed
        raise

    print(f"Created {path} with {len(BOOKS)} books by {len(AUTHORS)} authors.")


if __name__ == "__main__":
    main()
