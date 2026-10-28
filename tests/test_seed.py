import pytest

from scripts import seed_library
from src import library_service


def test_seed_creates_the_whole_library(tmp_path):
    path = tmp_path / "library.db"

    seed_library.seed(path)

    assert len(library_service.list_books(path)) == len(seed_library.BOOKS)
    assert len(library_service.list_authors(path)) == len(seed_library.AUTHORS)
    assert set(seed_library.GENRES) <= set(library_service.list_genres(path))


def test_an_author_with_books_in_two_languages_is_one_author(tmp_path):
    path = tmp_path / "library.db"
    seed_library.seed(path)

    overview = {names: books for _, names, _, books in library_service.list_authors_overview(path)}

    assert overview["Fredrik Backman / Фредерик Бакман"] == 2
    assert overview["Robin Hobb / Робин Хобб"] == 3
    assert overview["Брендон Сандерсон"] == 4


def test_every_seed_book_uses_a_known_author_and_has_a_publisher():
    for book in seed_library.BOOKS:
        assert book["publisher"]
        assert all(key in seed_library.AUTHORS for key in book["authors"])


def test_seed_refuses_to_touch_an_existing_file(tmp_path, monkeypatch, capsys):
    path = tmp_path / "library.db"
    path.write_bytes(b"my precious data")
    monkeypatch.setattr("sys.argv", ["seed_library", str(path)])

    with pytest.raises(SystemExit):
        seed_library.main()

    assert path.read_bytes() == b"my precious data"
    assert "already exists" in capsys.readouterr().out


def test_main_creates_a_new_database(tmp_path, monkeypatch, capsys):
    path = tmp_path / "new.db"
    monkeypatch.setattr("sys.argv", ["seed_library", str(path)])

    seed_library.main()

    assert path.exists()
    assert f"{len(seed_library.BOOKS)} books" in capsys.readouterr().out
