import tkinter as tk
from tkinter import ttk, messagebox

from src.library_service import add_new_book
from src.genre_service import get_all_genres
from src.author_service import get_all_author_names
from src.series_service import get_all_series


window = tk.Tk()
window.title("Personal Library")
window.geometry("650x600")


# -------------------------
# Add book
# -------------------------

add_book_label = tk.Label(
    window,
    text="Add book",
    font=("Arial", 16)
)
add_book_label.grid(
    row=0,
    column=0,
    columnspan=3,
    pady=15
)


# -------------------------
# Title
# -------------------------

title_label = tk.Label(
    window,
    text="Title:"
)
title_label.grid(
    row=1,
    column=0,
    padx=10,
    pady=5,
    sticky="e"
)

title_entry = tk.Entry(
    window,
    width=30
)
title_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=5,
    sticky="w"
)


# -------------------------
# Authors
# -------------------------

author_label = tk.Label(
    window,
    text="Author:"
)
author_label.grid(
    row=2,
    column=0,
    padx=10,
    pady=5,
    sticky="ne"
)

author_frame = tk.Frame(window)
author_frame.grid(
    row=2,
    column=1,
    columnspan=2,
    padx=10,
    pady=5,
    sticky="w"
)

author_comboboxes = []

authors = get_all_author_names()
author_names = [author[1] for author in authors]

# New authors are kept only until the book is saved.
new_authors = {}


def remove_author(author_combobox, remove_button):
    author_combobox.destroy()
    remove_button.destroy()

    author_comboboxes.remove(
        (author_combobox, remove_button)
    )

    for row, (combobox, button) in enumerate(
        author_comboboxes[1:],
        start=1
    ):
        combobox.grid(
            row=row,
            column=0,
            pady=2,
            sticky="w"
        )

        button.grid(
            row=row,
            column=1,
            padx=5,
            sticky="n"
        )


def add_author():
    row = len(author_comboboxes)

    new_author_combobox = ttk.Combobox(
        author_frame,
        values=author_names,
        state="readonly",
        width=28
    )
    new_author_combobox.grid(
        row=row,
        column=0,
        pady=2,
        sticky="w"
    )

    remove_button = tk.Button(
        author_frame,
        text="−",
        command=lambda: remove_author(
            new_author_combobox,
            remove_button
        )
    )
    remove_button.grid(
        row=row,
        column=1,
        padx=5,
        sticky="n"
    )

    author_comboboxes.append(
        (new_author_combobox, remove_button)
    )


def add_new_author():
    new_author_window = tk.Toplevel(window)
    new_author_window.title("Add new author")
    new_author_window.geometry("300x220")

    name_label = tk.Label(
        new_author_window,
        text="Name:"
    )
    name_label.pack(
        pady=(15, 5)
    )

    name_entry = tk.Entry(
        new_author_window,
        width=25
    )
    name_entry.pack()

    country_label = tk.Label(
        new_author_window,
        text="Country:"
    )
    country_label.pack(
        pady=(10, 5)
    )

    countries = [
        "Canada",
        "Czech Republic",
        "France",
        "Germany",
        "Japan",
        "Poland",
        "Russia",
        "Scotland",
        "Sweden",
        "United States"
    ]

    country_combobox = ttk.Combobox(
        new_author_window,
        values=countries,
        width=22
    )
    country_combobox.pack()

    def save_author_for_book():
        name = name_entry.get().strip()
        country = country_combobox.get().strip()

        if not name:
            messagebox.showwarning(
                "Empty field",
                "Please enter author's name."
            )
            return

        if not country:
            messagebox.showwarning(
                "Empty field",
                "Please enter author's country."
            )
            return

        if name in author_names:
            messagebox.showwarning(
                "Author already exists",
                "This author is already in the list."
            )
            return

        new_authors[name] = country
        author_names.append(name)

        for combobox, button in author_comboboxes:
            combobox["values"] = author_names

        new_author_window.destroy()

    save_button = tk.Button(
        new_author_window,
        text="Add",
        command=save_author_for_book
    )
    save_button.pack(
        pady=15
    )


author_combobox = ttk.Combobox(
    author_frame,
    values=author_names,
    state="readonly",
    width=28
)
author_combobox.grid(
    row=0,
    column=0,
    pady=2,
    sticky="w"
)

author_comboboxes.append(
    (author_combobox, None)
)


add_author_button = tk.Button(
    author_frame,
    text="+",
    command=add_author
)
add_author_button.grid(
    row=0,
    column=1,
    padx=5,
    sticky="n"
)


new_author_button = tk.Button(
    author_frame,
    text="Add new author",
    command=add_new_author
)
new_author_button.grid(
    row=0,
    column=2,
    padx=5,
    sticky="n"
)


# -------------------------
# Publisher
# -------------------------

publisher_label = tk.Label(
    window,
    text="Publisher:"
)
publisher_label.grid(
    row=3,
    column=0,
    padx=10,
    pady=5,
    sticky="e"
)

publishers = [
    "Alpress",
    "Argo",
    "Corpus",
    "HarperCollins",
    "Laser",
    "Scholastic",
    "Simon & Schuster",
    "Азбука",
    "Иностранка",
    "Синдбад",
    "АСТ"
]

publisher_combobox = ttk.Combobox(
    window,
    values=publishers,
    width=28
)
publisher_combobox.grid(
    row=3,
    column=1,
    padx=10,
    pady=5,
    sticky="w"
)


# -------------------------
# Language
# -------------------------

language_label = tk.Label(
    window,
    text="Language:"
)
language_label.grid(
    row=4,
    column=0,
    padx=10,
    pady=5,
    sticky="e"
)

language_combobox = ttk.Combobox(
    window,
    values=["ru", "cs", "en"],
    state="readonly",
    width=28
)
language_combobox.grid(
    row=4,
    column=1,
    padx=10,
    pady=5,
    sticky="w"
)


# -------------------------
# Series
# -------------------------

series_label = tk.Label(
    window,
    text="Series:"
)
series_label.grid(
    row=5,
    column=0,
    padx=10,
    pady=5,
    sticky="e"
)

series_names = get_all_series()

series_combobox = ttk.Combobox(
    window,
    values=series_names,
    width=28
)
series_combobox.grid(
    row=5,
    column=1,
    padx=10,
    pady=5,
    sticky="w"
)


# -------------------------
# Volume number
# -------------------------

volume_label = tk.Label(
    window,
    text="Volume number:"
)
volume_label.grid(
    row=6,
    column=0,
    padx=10,
    pady=5,
    sticky="e"
)

volume_entry = tk.Entry(
    window,
    width=10
)
volume_entry.grid(
    row=6,
    column=1,
    padx=10,
    pady=5,
    sticky="w"
)


# -------------------------
# Genres
# -------------------------

genre_label = tk.Label(
    window,
    text="Genre:"
)
genre_label.grid(
    row=7,
    column=0,
    padx=10,
    pady=5,
    sticky="ne"
)

genre_frame = tk.Frame(window)
genre_frame.grid(
    row=7,
    column=1,
    columnspan=2,
    padx=10,
    pady=5,
    sticky="w"
)

genre_comboboxes = []

genre_names = get_all_genres()

# New genres are kept only until the book is saved.
new_genres = []


def remove_genre(genre_combobox, remove_button):
    genre_combobox.destroy()
    remove_button.destroy()

    genre_comboboxes.remove(
        (genre_combobox, remove_button)
    )

    for row, (combobox, button) in enumerate(
        genre_comboboxes[1:],
        start=1
    ):
        combobox.grid(
            row=row,
            column=0,
            pady=2,
            sticky="w"
        )

        button.grid(
            row=row,
            column=1,
            padx=5,
            sticky="n"
        )


def add_genre():
    row = len(genre_comboboxes)

    new_genre_combobox = ttk.Combobox(
        genre_frame,
        values=genre_names,
        state="readonly",
        width=28
    )
    new_genre_combobox.grid(
        row=row,
        column=0,
        pady=2,
        sticky="w"
    )

    remove_button = tk.Button(
        genre_frame,
        text="−",
        command=lambda: remove_genre(
            new_genre_combobox,
            remove_button
        )
    )
    remove_button.grid(
        row=row,
        column=1,
        padx=5,
        sticky="n"
    )

    genre_comboboxes.append(
        (new_genre_combobox, remove_button)
    )


def add_new_genre():
    new_genre_window = tk.Toplevel(window)
    new_genre_window.title("Add new genre")
    new_genre_window.geometry("300x150")

    genre_name_label = tk.Label(
        new_genre_window,
        text="Genre name:"
    )
    genre_name_label.pack(
        pady=(15, 5)
    )

    genre_name_entry = tk.Entry(
        new_genre_window,
        width=25
    )
    genre_name_entry.pack()

    def save_genre_for_book():
        genre_name = genre_name_entry.get().strip()

        if not genre_name:
            messagebox.showwarning(
                "Empty field",
                "Please enter a genre name."
            )
            return

        if genre_name in genre_names:
            messagebox.showwarning(
                "Genre already exists",
                "This genre is already in the list."
            )
            return

        new_genres.append(genre_name)
        genre_names.append(genre_name)

        for combobox, button in genre_comboboxes:
            combobox["values"] = genre_names

        new_genre_window.destroy()

    save_button = tk.Button(
        new_genre_window,
        text="Add",
        command=save_genre_for_book
    )
    save_button.pack(
        pady=15
    )


genre_combobox = ttk.Combobox(
    genre_frame,
    values=genre_names,
    state="readonly",
    width=28
)
genre_combobox.grid(
    row=0,
    column=0,
    pady=2,
    sticky="w"
)

genre_comboboxes.append(
    (genre_combobox, None)
)


add_genre_button = tk.Button(
    genre_frame,
    text="+",
    command=add_genre
)
add_genre_button.grid(
    row=0,
    column=1,
    padx=5,
    sticky="n"
)


new_genre_button = tk.Button(
    genre_frame,
    text="Add new genre",
    command=add_new_genre
)
new_genre_button.grid(
    row=0,
    column=2,
    padx=5,
    sticky="n"
)


def clear_form():
    # Title
    title_entry.delete(0, tk.END)

    # Author
    for combobox, button in author_comboboxes:
        combobox.destroy()
        if button is not None:
            button.destroy()

    author_comboboxes.clear()

    author_combobox = ttk.Combobox(
        author_frame,
        values=author_names,
        state="readonly",
        width=28
    )
    author_combobox.grid(
        row=0,
        column=0,
        pady=2,
        sticky="w"
    )

    author_comboboxes.append(
        (author_combobox, None)
    )

    # Publisher
    publisher_combobox.set("")

    # Language
    language_combobox.set("")

    # Series
    series_combobox.set("")

    # Volume number
    volume_entry.delete(0, tk.END)

    # Genre
    for combobox, button in genre_comboboxes:
        combobox.destroy()
        if button is not None:
            button.destroy()

    genre_comboboxes.clear()

    genre_combobox = ttk.Combobox(
        genre_frame,
        values=genre_names,
        state="readonly",
        width=28
    )
    genre_combobox.grid(
        row=0,
        column=0,
        pady=2,
        sticky="w"
    )

    genre_comboboxes.append(
        (genre_combobox, None)
    )

    new_authors.clear()
    new_genres.clear()


# -------------------------
# Save book
# -------------------------

def save_book():
    title = title_entry.get().strip()
    language = language_combobox.get().strip()
    publisher = publisher_combobox.get().strip()
    series_name = series_combobox.get().strip()
    volume_number = volume_entry.get().strip()

    if not title:
        messagebox.showwarning(
            "Empty field",
            "Please enter a book title."
        )
        return

    if not language:
        messagebox.showwarning(
            "Empty field",
            "Please select a language."
        )
        return

    authors_for_book = []

    for combobox, button in author_comboboxes:
        author_name = combobox.get().strip()

        if not author_name:
            continue

        country = new_authors.get(
            author_name,
            ""
        )

        authors_for_book.append(
            {
                "name": author_name,
                "country": country
            }
        )

    if not authors_for_book:
        messagebox.showwarning(
            "No author",
            "Please select at least one author."
        )
        return

    genres_for_book = []

    for combobox, button in genre_comboboxes:
        genre_name = combobox.get().strip()

        if genre_name:
            genres_for_book.append(genre_name)

    if not series_name:
        series_name = None

    if not volume_number:
        volume_number = None
    else:
        try:
            volume_number = int(volume_number)
        except ValueError:
            messagebox.showwarning(
                "Invalid volume number",
                "Volume number must be a number."
            )
            return

    try:
        book_id = add_new_book(
            title=title,
            language=language,
            authors=authors_for_book,
            genres=genres_for_book,
            publisher=publisher or None,
            series_name=series_name,
            volume_number=volume_number
        )

    except ValueError as error:
        messagebox.showerror(
            "Could not add book",
            str(error)
        )
        return

    messagebox.showinfo(
        "Book added",
        f"Book added successfully.\nBook ID: {book_id}"
    )

    clear_form()


add_book_button = tk.Button(
    window,
    text="Add book",
    command=save_book
)
add_book_button.grid(
    row=8,
    column=0,
    columnspan=3,
    pady=20
)


window.mainloop()