# Personal Library

A personal library management application written in Python using SQLite.

## About the project

The goal is to build an application for managing my personal book collection rather than a reading tracker.

The catalog is based on physical editions rather than bibliographic records. Book information reflects the specific editions in my collection, including their titles, publishers and languages.

The application will allow me to:

- store information about books;
- organize authors and book series;
- search by title, author, language, publisher and country;
- mark whether a book has been read;
- keep my library organized.

This project is also a way to practice Python, SQL and database design by solving a real-world problem.

## Design principles

The application is designed around books.

Users interact only with books. Related entities such as authors, publishers and book series are created or linked automatically when needed.

## Technologies

- Python
- SQLite
- SQL
- Git
- PyCharm

## Planned features

- Book series
- Genres
- Book status (read / unread / reading)
- User interface

## Search improvements

- Ignore case
- Ignore dots in initials
- Ignore duplicate spaces
- Normalize author names
- Normalize book titles

## User experience

- Autocomplete suggestions for authors, publishers and series
- Simple book-oriented interface