# Database Schema

The source of truth is `sql/create_tables.sql`. Foreign keys are enforced (`PRAGMA foreign_keys = ON` in `get_connection`).

## Authors

- author_id (PK)
- country

## AuthorNames

- author_name_id (PK)
- author_id (FK → Authors, ON DELETE CASCADE)
- language (NOT NULL)
- name (NOT NULL)
- name_normalized (NOT NULL)

UNIQUE (author_id, language): an author has at most one name per language.

## Series

- series_id (PK)
- series_name (NOT NULL, UNIQUE)
- series_name_normalized (NOT NULL)

## Books

- book_id (PK)
- title (NOT NULL)
- title_normalized (NOT NULL)
- language (NOT NULL)
- series_id (FK → Series, nullable)
- volume_number (nullable)
- publisher (nullable)

## BookAuthors

- book_id (FK → Books, ON DELETE CASCADE)
- author_id (FK → Authors)

PRIMARY KEY (book_id, author_id)

## Users

- user_id (PK)
- user_name (NOT NULL, UNIQUE)

## UserBooks

- user_id (FK → Users)
- book_id (FK → Books, ON DELETE CASCADE)
- is_read (NOT NULL, default 0)

PRIMARY KEY (user_id, book_id)

## Genres

- genre_id (PK)
- genre_name (NOT NULL, UNIQUE)

## BookGenres

- book_id (FK → Books, ON DELETE CASCADE)
- genre_id (FK → Genres)

PRIMARY KEY (book_id, genre_id)

## Design Principles

- The `books` table stores physical book copies rather than literary works: the Russian and English editions of the same novel are separate books.
- A book may have multiple authors.
- An author is one person with one name per language (for example "Антон Чехов" in `ru` and "Anton Chekhov" in `en`). This lets one author be counted across all languages.
- A series may contain multiple books.
- Reading status is stored per user, not per book.
- Searchable text (titles, author names, series names) is stored twice: the original and a `*_normalized` column (lower case, dots replaced by spaces, repeated spaces collapsed). Search runs on the normalized columns, so every insert must fill them.
- Deleting a book removes its links automatically; authors, series and genres that no longer have any books are removed by `book_service.delete_book`.
- There are no migrations yet. `initialize_database` runs `CREATE TABLE` statements and is meant for creating a new database only.
