# Personal Library

A personal library management application written in Python using SQLite and Tkinter.

## About the project

The goal is to build an application for managing my personal book collection rather than a reading tracker.

The catalog is based on physical editions rather than bibliographic records. Book information reflects the specific editions in my collection, including their titles, publishers and languages.

The application lets me:

- add and delete books;
- keep authors, book series and genres organized;
- give an author a name in each language, so one author is counted once across all editions.

This project is also a way to practice Python, SQL and database design by solving a real-world problem. Once the database is filled, a small data-analysis part is planned (books per author, books per language).

## Design principles

The application is designed around books.

Users interact only with books. Related entities such as authors, publishers and book series are created or linked automatically when a book is added. An author that already exists is chosen from a list instead.

## Running

Developed with Python 3.13 (Tkinter and SQLite come with it). From the project root:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the app (opens a demo database `data/demo.db`, created on first run):

```
python -m ui.ui
```

Run the tests (they use temporary databases):

```
python -m pytest
```

The full database schema is described in `schema.md`.

## Technologies

- Python
- SQLite
- SQL
- Tkinter
- pytest
- Git
- PyCharm / VS Code

## Implemented

- Books with title, language, publisher, series and volume number
- Authors with one name per language; several authors per book
- Series and genres, created together with a book
- Duplicate book detection
- Normalized text for search (ignores case, dots in initials and extra spaces)
- Tkinter interface: add a book, add a new author, add a name in another language to an existing author, manage and delete books (sortable table)

## Planned features

- Search in the interface (the search functions currently cover title, author and series)
- Search by language, publisher and country
- Book status (read / unread / reading)
- Autocomplete suggestions for authors, publishers and series
- Data analysis once the database is filled
