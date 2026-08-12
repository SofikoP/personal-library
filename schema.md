# Database Schema

## Authors

- author_id (PK)
- country

## AuthorNames

- author_name_id (PK)
- author_id (FK → Authors)
- name

## Series

- series_id (PK)
- series_name

## Books

- book_id (PK)
- title
- language
- series_id (FK → Series, nullable)
- volume_number (nullable)
- publisher

## BookAuthors

- book_id 
- author_id

PRIMARY KEY (book_id, author_id)

## Users

- user_id (PK)
- username

## UserBooks

- user_id (FK → Users)
- book_id (FK → Books)
- is_read

PRIMARY KEY (user_id, book_id)

## Genres
- genre_id (PK)
- genre_name

## BookGenres

- book_id 
- genre_id

PRIMARY KEY (book_id, genre_id)

## Design Principles

- The `books` table stores physical book copies rather than literary works.
- A book may have multiple authors.
- An author may have multiple localized names.
- A series may contain multiple books.
- Reading status is stored per user, not per book.