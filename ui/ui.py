import itertools
import sqlite3
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

from scripts.demo_db import create_demo_database
from src import library_service as library
from src.database import DB_PATH

LANGUAGES = ["ru", "cs", "en"]

COUNTRIES = [
    "Canada", "Czech Republic", "France", "Germany", "Japan",
    "Poland", "Russia", "Scotland", "Sweden", "United States",
]

PUBLISHERS = [
    "Alpress", "Argo", "Corpus", "HarperCollins", "Laser", "Scholastic",
    "Simon & Schuster", "Азбука", "Иностранка", "Синдбад", "АСТ",
]


BG = "#F2EADC"
FIELD = "#D9DDE2"
TEXT = "#2b2b2b"
MUTED = "#4a5d72"
BORDER = "#97A9BC"
BUTTON = "#A4B9CE"
BUTTON_HOVER = "#93AAC2"
TABLE = "#F4F7FA"
ACCENT = "#51121A"
ACCENT_HOVER = "#3A0C12"
DANGER = "#a3141f"

FONT = ("Segoe UI Semibold", 10)


def apply_style(root):
    """One look for the whole app: warm light background, flat buttons, roomy fields."""
    root.configure(background=BG)

    # semibold text everywhere (entries, dropdowns, table, dialogs)
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        tkfont.nametofont(name).configure(family="Segoe UI Semibold", size=10)

    root.option_add("*TCombobox*Listbox.font", FONT)
    root.option_add("*TCombobox*Listbox.background", BG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", font=FONT, background=BG, foreground=TEXT)
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG)
    style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground=ACCENT)
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("TSeparator", background=BORDER)

    field = dict(fieldbackground=FIELD, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=6)
    style.configure("TEntry", **field)
    style.configure("TCombobox", arrowcolor=MUTED, **field)
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", FIELD)],
        bordercolor=[("focus", ACCENT)],
        # a chosen value in a read-only dropdown is drawn "selected" by default (light text on a dark box)
        selectbackground=[("readonly", FIELD)],
        selectforeground=[("readonly", TEXT)],
        foreground=[("readonly", TEXT)],
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    button = dict(padding=(12, 6), relief="flat", borderwidth=1, bordercolor=BORDER,
                  lightcolor=BUTTON, darkcolor=BUTTON, focuscolor=BUTTON)
    style.configure("TButton", background=BUTTON, **button)
    style.map("TButton", background=[("active", BUTTON_HOVER)], lightcolor=[("active", BUTTON_HOVER)],
              darkcolor=[("active", BUTTON_HOVER)])

    style.configure("Small.TButton", padding=(8, 3))

    accent = dict(button, padding=(28, 10), bordercolor=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT, focuscolor=ACCENT)
    style.configure("Accent.TButton", background=ACCENT, foreground="white", font=("Segoe UI", 11, "bold"), **accent)
    style.map("Accent.TButton", background=[("active", ACCENT_HOVER)], lightcolor=[("active", ACCENT_HOVER)],
              darkcolor=[("active", ACCENT_HOVER)])

    style.configure("Danger.TButton", foreground=DANGER)

    style.configure("Treeview", background=TABLE, fieldbackground=TABLE, rowheight=28,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
    style.configure("Treeview.Heading", background=BUTTON, font=("Segoe UI", 10, "bold"), padding=6, relief="flat")
    style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])


def add_clear_button(widget):
    """Show a small "×" inside an entry/dropdown while it has text; clicking it empties the field."""
    variable = tk.StringVar()
    widget.configure(textvariable=variable)

    # a dropdown has an arrow on the right, so the "×" sits left of it
    offset = 28 if isinstance(widget, ttk.Combobox) else 8

    button = tk.Label(
        widget, text="×", font=("Segoe UI", 11), padx=2, pady=0, borderwidth=0,
        background=FIELD, foreground=TEXT, cursor="hand2",
    )
    button.bind("<Button-1>", lambda event: variable.set(""))
    button.bind("<Enter>", lambda event: button.configure(foreground=ACCENT))
    button.bind("<Leave>", lambda event: button.configure(foreground=TEXT))

    def update(*_):
        if variable.get():
            button.place(relx=1.0, x=-offset, y=-2, rely=0.5, anchor="e")
        else:
            button.place_forget()

    variable.trace_add("write", update)
    return widget


class ChoiceList(ttk.Frame):
    """A column of dropdowns (used for authors and genres).

    The first row has a "+" button that adds another row; added rows have a "−" button to remove them.
    """

    def __init__(self, parent, values=()):
        super().__init__(parent)
        self.values = list(values)
        self.rows = []  # (row_frame, combobox)
        self.add_row()

    def add_row(self, extra=False):
        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x", pady=3)

        combobox = add_clear_button(ttk.Combobox(row_frame, values=self.values, state="readonly", width=40))
        combobox.pack(side="left", fill="x", expand=True)

        if extra:
            button = ttk.Button(
                row_frame, text="−", width=3, style="Small.TButton",
                command=lambda: self.remove_row(row_frame, combobox),
            )
        else:
            button = ttk.Button(
                row_frame, text="+", width=3, style="Small.TButton",
                command=lambda: self.add_row(extra=True),
            )

        button.pack(side="left", padx=(8, 0))

        self.rows.append((row_frame, combobox))

    def remove_row(self, row_frame, combobox):
        self.rows.remove((row_frame, combobox))
        row_frame.destroy()

    def set_values(self, values):
        self.values = list(values)

        for _, combobox in self.rows:
            combobox["values"] = self.values

    def select(self, value):
        """Put value into the first empty row (add a row if all are filled)."""
        for _, combobox in self.rows:
            if not combobox.get():
                combobox.set(value)
                return

        self.add_row(extra=True)
        self.rows[-1][1].set(value)

    def selected(self):
        """Non-empty choices without repeats, in the order shown."""
        chosen = []

        for _, combobox in self.rows:
            value = combobox.get().strip()

            if value and value not in chosen:
                chosen.append(value)

        return chosen

    def reset(self):
        for row_frame, _ in self.rows:
            row_frame.destroy()

        self.rows.clear()
        self.add_row()


class LibraryApp:
    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path

        # label shown in the dropdown -> what add_new_book expects for that author
        self.author_choices = {}
        # authors typed in "New author" that are saved together with the book
        self.pending_authors = {}
        self.pending_genres = []

        self.build_form()
        self.load_lists()

    # -------------------------
    # Form
    # -------------------------

    def build_form(self):
        form = ttk.Frame(self.root, padding=(30, 20, 30, 20))
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        rows = itertools.count()

        ttk.Label(form, text="Add book", style="Title.TLabel").grid(
            row=next(rows), column=0, columnspan=2, sticky="w"
        )

        # Book
        self.add_section(form, next(rows), "Book")
        self.title_entry = self.add_field(form, next(rows), "Title", ttk.Entry(form))

        self.author_list = ChoiceList(form)
        self.add_field(form, next(rows), "Authors", self.author_list, top=True)

        author_buttons = ttk.Frame(form)
        author_buttons.grid(row=next(rows), column=1, sticky="w", pady=(2, 0))
        ttk.Button(author_buttons, text="Add new author", style="Small.TButton",
                   command=self.open_new_author).pack(side="left")
        ttk.Button(author_buttons, text="Add name to author", style="Small.TButton",
                   command=self.open_add_author_name).pack(side="left", padx=6)

        # Edition
        self.add_section(form, next(rows), "Edition")
        self.publisher_combobox = self.add_field(
            form, next(rows), "Publisher", ttk.Combobox(form, values=PUBLISHERS)
        )
        self.language_combobox = self.add_field(
            form, next(rows), "Language", ttk.Combobox(form, values=LANGUAGES, state="readonly")
        )
        self.series_combobox = self.add_field(form, next(rows), "Series", ttk.Combobox(form))
        digits_only = (self.root.register(lambda text: text == "" or (text.isascii() and text.isdigit())), "%P")
        self.volume_entry = self.add_field(
            form, next(rows), "Volume number",
            ttk.Entry(form, width=8, validate="key", validatecommand=digits_only),
            narrow=True,
        )

        # Genres
        self.add_section(form, next(rows), "Genres")
        self.genre_list = ChoiceList(form)
        self.add_field(form, next(rows), "Genres", self.genre_list, top=True)

        genre_buttons = ttk.Frame(form)
        genre_buttons.grid(row=next(rows), column=1, sticky="w", pady=(2, 0))
        ttk.Button(genre_buttons, text="Add new genre", style="Small.TButton",
                   command=self.open_new_genre).pack(side="left")

        # Actions
        actions = ttk.Frame(form)
        actions.grid(row=next(rows), column=0, columnspan=2, sticky="ew", pady=(28, 0))
        ttk.Button(actions, text="Save book", style="Accent.TButton", command=self.save_book).pack(side="left")
        ttk.Button(actions, text="Manage books", command=self.open_manage_books).pack(side="left", padx=12)

        ttk.Label(form, text=f"Database: {self.db_path.name}", style="Muted.TLabel").grid(
            row=next(rows), column=0, columnspan=2, sticky="w", pady=(18, 0)
        )

    @staticmethod
    def add_section(form, row, title):
        """A bold heading with a thin line under it."""
        section = ttk.Frame(form)
        section.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(22, 6))
        ttk.Label(section, text=title, style="Section.TLabel").pack(anchor="w")
        ttk.Separator(section).pack(fill="x", pady=(4, 0))

    @staticmethod
    def add_field(form, row, label, widget, top=False, narrow=False):
        """Place "label  widget" on one row of the form and return the widget."""
        ttk.Label(form, text=label).grid(
            row=row, column=0, padx=(0, 18), pady=6, sticky="nw" if top else "w"
        )
        if isinstance(widget, (ttk.Entry, ttk.Combobox)):
            add_clear_button(widget)

        widget.grid(row=row, column=1, pady=6, sticky="w" if narrow else "ew")
        return widget

    def load_lists(self):
        """Refresh every dropdown from the database."""
        self.author_choices = {
            label: {"author_id": author_id}
            for author_id, label in library.list_authors(self.db_path)
        }
        self.author_choices.update(self.pending_authors)
        self.author_list.set_values(sorted(self.author_choices, key=str.casefold))

        self.series_combobox["values"] = library.list_series(self.db_path)

        genres = library.list_genres(self.db_path) + self.pending_genres
        self.genre_list.set_values(sorted(genres, key=str.casefold))

    def reset_form(self):
        self.title_entry.delete(0, tk.END)
        self.author_list.reset()
        self.publisher_combobox.set("")
        self.language_combobox.set("")
        self.series_combobox.set("")
        self.volume_entry.delete(0, tk.END)
        self.genre_list.reset()

        self.pending_authors.clear()
        self.pending_genres.clear()
        self.load_lists()

    # -------------------------
    # Small dialogs
    # -------------------------

    def make_dialog(self, title):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(background=BG)
        dialog.transient(self.root)
        dialog.grab_set()

        body = ttk.Frame(dialog, padding=22)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        return dialog, body

    def open_new_author(self):
        dialog, body = self.make_dialog("New author")

        name_entry = self.add_field(body, 0, "Name:", ttk.Entry(body, width=30))
        country_combobox = self.add_field(body, 1, "Country:", ttk.Combobox(body, values=COUNTRIES, width=27))
        language_combobox = self.add_field(
            body, 2, "Name language:", ttk.Combobox(body, values=LANGUAGES, state="readonly", width=27)
        )

        def add():
            name = name_entry.get().strip()
            country = country_combobox.get().strip()
            language = language_combobox.get().strip()

            if not name or not country or not language:
                messagebox.showwarning("Empty field", "Please fill in name, country and name language.", parent=dialog)
                return

            if any(name in label.split(" / ") for label in self.author_choices):
                messagebox.showwarning(
                    "Author already exists",
                    "This author is already in the list.\nUse \"Add name to author\" to add a name in another language.",
                    parent=dialog,
                )
                return

            label = f"{name} (new)"
            self.pending_authors[label] = {"name": name, "country": country, "language": language}
            self.load_lists()
            self.author_list.select(label)
            dialog.destroy()

        ttk.Button(body, text="Add", style="Accent.TButton", command=add).grid(
            row=3, column=0, columnspan=2, sticky="e", pady=(14, 0)
        )

    def open_add_author_name(self):
        existing = {label: author_id for author_id, label in library.list_authors(self.db_path)}

        if not existing:
            messagebox.showinfo("No authors", "There are no saved authors yet.")
            return

        dialog, body = self.make_dialog("Add name to author")

        author_combobox = self.add_field(
            body, 0, "Author:", ttk.Combobox(body, values=list(existing), state="readonly", width=40)
        )
        name_entry = self.add_field(body, 1, "Name:", ttk.Entry(body, width=43))
        language_combobox = self.add_field(
            body, 2, "Name language:", ttk.Combobox(body, values=LANGUAGES, state="readonly", width=40)
        )

        def save():
            label = author_combobox.get()
            name = name_entry.get().strip()
            language = language_combobox.get()

            if not label or not name or not language:
                messagebox.showwarning("Empty field", "Please fill in all fields.", parent=dialog)
                return

            try:
                library.add_author_name(existing[label], name, language, db_path=self.db_path)
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Could not add name",
                    "This author already has a name in that language.",
                    parent=dialog,
                )
                return

            self.load_lists()
            dialog.destroy()

        ttk.Button(body, text="Save", style="Accent.TButton", command=save).grid(
            row=3, column=0, columnspan=2, sticky="e", pady=(14, 0)
        )

    def open_new_genre(self):
        dialog, body = self.make_dialog("New genre")

        name_entry = self.add_field(body, 0, "Genre name:", ttk.Entry(body, width=30))

        def add():
            name = name_entry.get().strip()

            if not name:
                messagebox.showwarning("Empty field", "Please enter a genre name.", parent=dialog)
                return

            if name in self.genre_list.values:
                messagebox.showwarning("Genre already exists", "This genre is already in the list.", parent=dialog)
                return

            self.pending_genres.append(name)
            self.load_lists()
            self.genre_list.select(name)
            dialog.destroy()

        ttk.Button(body, text="Add", style="Accent.TButton", command=add).grid(
            row=1, column=0, columnspan=2, sticky="e", pady=(14, 0)
        )

    # -------------------------
    # Save book
    # -------------------------

    def save_book(self):
        title = self.title_entry.get().strip()
        language = self.language_combobox.get().strip()
        publisher = self.publisher_combobox.get().strip()
        series_name = self.series_combobox.get().strip()
        volume_text = self.volume_entry.get().strip()

        if not title:
            messagebox.showwarning("Empty field", "Please enter a book title.")
            return

        if not language:
            messagebox.showwarning("Empty field", "Please select a language.")
            return

        author_labels = self.author_list.selected()

        if not author_labels:
            messagebox.showwarning("No author", "Please select at least one author.")
            return

        volume_number = None

        if volume_text:
            try:
                volume_number = int(volume_text)
            except ValueError:
                messagebox.showwarning("Invalid volume number", "Volume number must be a number.")
                return

        try:
            book_id = library.add_new_book(
                title=title,
                language=language,
                authors=[self.author_choices[label] for label in author_labels],
                genres=self.genre_list.selected(),
                publisher=publisher or None,
                series_name=series_name or None,
                volume_number=volume_number,
                db_path=self.db_path,
            )
        except (ValueError, sqlite3.IntegrityError) as error:
            messagebox.showerror("Could not add book", str(error))
            return

        messagebox.showinfo("Book added", f"Book added successfully.\nBook ID: {book_id}")
        self.reset_form()

    # -------------------------
    # Manage / delete books
    # -------------------------

    def open_manage_books(self):
        window = tk.Toplevel(self.root)
        window.title("Manage books")
        window.geometry("1130x480")
        window.configure(background=BG)

        ttk.Label(window, text="Select a book to delete it", style="Muted.TLabel").pack(
            anchor="w", padx=20, pady=(16, 8)
        )

        columns = {
            "book_id": ("ID", 45),
            "title": ("Title", 270),
            "authors": ("Authors", 270),
            "series": ("Series", 150),
            "volume": ("Volume", 65),
            "language": ("Language", 70),
            "publisher": ("Publisher", 130),
        }

        buttons = ttk.Frame(window)
        buttons.pack(side="bottom", fill="x", padx=20, pady=16)

        tree = ttk.Treeview(window, columns=list(columns), show="headings", selectmode="browse")
        for column, (heading, width) in columns.items():
            tree.heading(column, text=heading, anchor="w", command=lambda column=column: sort_by(column))
            tree.column(column, width=width, anchor="w")

        loaded_rows = []  # the books as last read from the database
        sort = {"column": "title", "descending": False}

        scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=5)
        scrollbar.pack(side="left", fill="y", pady=5, padx=(0, 20))

        def show_rows():
            """Fill the table from loaded_rows in the chosen order (empty values always go last)."""
            selected = tree.selection()
            selected_id = tree.item(selected[0], "values")[0] if selected else None

            index = list(columns).index(sort["column"])
            filled = [row for row in loaded_rows if row[index] != ""]
            empty = [row for row in loaded_rows if row[index] == ""]

            if sort["column"] in ("book_id", "volume"):
                filled.sort(key=lambda row: int(row[index]), reverse=sort["descending"])
            else:
                filled.sort(key=lambda row: str(row[index]).casefold(), reverse=sort["descending"])

            tree.delete(*tree.get_children())

            for row in filled + empty:
                item = tree.insert("", "end", values=row)

                if str(row[0]) == selected_id:
                    tree.selection_set(item)

            for column, (heading, _) in columns.items():
                arrow = ""

                if column == sort["column"]:
                    arrow = "  ▼" if sort["descending"] else "  ▲"

                tree.heading(column, text=heading + arrow)

        def sort_by(column):
            sort["descending"] = not sort["descending"] if sort["column"] == column else False
            sort["column"] = column
            show_rows()

        def refresh():
            loaded_rows[:] = [
                ["" if value is None else value for value in row]
                for row in library.list_books(self.db_path)
            ]
            show_rows()

        def delete_selected():
            selection = tree.selection()

            if not selection:
                messagebox.showwarning("No book selected", "Please select a book first.", parent=window)
                return

            book_id, title = tree.item(selection[0], "values")[:2]

            if not messagebox.askyesno(
                "Confirm deletion",
                f"Delete '{title}' (ID: {book_id})?\nThis action cannot be undone.",
                parent=window,
            ):
                return

            library.delete_book(int(book_id), db_path=self.db_path)

            refresh()
            self.load_lists()  # authors/series/genres of the deleted book may be gone too

        ttk.Button(buttons, text="Delete selected book", style="Danger.TButton", command=delete_selected).pack(side="left")
        ttk.Button(buttons, text="Refresh list", command=refresh).pack(side="left", padx=10)

        refresh()


def schema_problem(db_path):
    """Return a message if db_path is not a database in the current schema, otherwise None."""
    if not db_path.exists():
        return f"Database file not found:\n{db_path}"

    connection = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)

    try:
        book_columns = [row[1] for row in connection.execute("PRAGMA table_info(books)")]
        name_columns = [row[1] for row in connection.execute("PRAGMA table_info(author_names)")]
    finally:
        connection.close()

    if "title_normalized" in book_columns and "language" in name_columns:
        return None

    return (
        f"{db_path.name} was created with an older version of the schema, "
        "so the app cannot work with it yet.\n\n"
        "Nothing was changed. Run the app without --real to use the demo database."
    )


def main():
    root = tk.Tk()
    root.title("Personal Library")
    apply_style(root)

    if "--real" in sys.argv:
        db_path = DB_PATH
        problem = schema_problem(db_path)

        if problem:
            root.withdraw()
            messagebox.showerror("Cannot open database", problem)
            return
    else:
        db_path = create_demo_database()

    LibraryApp(root, db_path)
    root.mainloop()


if __name__ == "__main__":
    main()
