CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,
    country TEXT
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    user_name TEXT NOT NULL UNIQUE
);

CREATE TABLE series (
    series_id INTEGER PRIMARY KEY,
    series_name TEXT NOT NULL,
    author_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    language TEXT NOT NULL,
    series_id INTEGER,
    volume_number INTEGER,
    publisher TEXT,
    FOREIGN KEY (series_id) REFERENCES series(series_id)
);

CREATE TABLE book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE author_names (
    author_name_id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    language TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    UNIQUE (author_id, language)
);

CREATE TABLE user_books (
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);