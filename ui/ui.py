import itertools
import sqlite3
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

from src import library_service as library
from src.database import DB_PATH
from src.demo_db import create_demo_database

LANGUAGES = ["ru", "cs", "en"]

COUNTRIES = [
    "Canada", "Czech Republic", "France", "Germany", "Japan",
    "Poland", "Russia", "Scotland", "Sweden", "United States",
]

PUBLISHERS = [
    "Alpress", "Argo", "Corpus", "HarperCollins", "Laser", "Scholastic",
    "Simon & Schuster", "Азбука", "Иностранка", "Синдбад", "АСТ",
]


def country_values(db_path):
    """Countries for a dropdown: the ready-made ones plus those already stored for authors."""
    stored = library.list_countries(db_path)
    known = {country.casefold() for country in COUNTRIES}

    return sorted(COUNTRIES + [country for country in stored if country.casefold() not in known], key=str.casefold)


def publisher_values(db_path):
    """Publishers for the dropdown: the ready-made ones plus those already stored for books."""
    stored = library.list_publishers(db_path)
    known = {publisher.casefold() for publisher in PUBLISHERS}

    return sorted(PUBLISHERS + [name for name in stored if name.casefold() not in known], key=str.casefold)


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


# Windows key codes of the physical keys V, C, X, A (they do not change with the keyboard layout)
CTRL_KEY_ACTIONS = {86: "<<Paste>>", 67: "<<Copy>>", 88: "<<Cut>>"}
KEY_A = 65


def on_ctrl_key(event):
    """Make Ctrl+V / C / X / A work in entries when a non-Latin layout (e.g. Russian) is active.

    Tk only knows these shortcuts by their Latin letters; with the Russian layout the same keys
    are other letters and nothing happens. With a Latin layout Tk already handles them, so we skip.
    """
    if event.keysym.lower() in ("v", "c", "x", "a"):
        return None

    widget = event.widget

    if not isinstance(widget, ttk.Entry):  # ttk.Combobox is an Entry too
        return None

    if event.keycode in CTRL_KEY_ACTIONS:
        widget.event_generate(CTRL_KEY_ACTIONS[event.keycode])
        return "break"

    if event.keycode == KEY_A:
        widget.selection_range(0, "end")
        widget.icursor("end")
        return "break"

    return None


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
    With editable=True the user may also type a value that is not in the list.
    """

    def __init__(self, parent, values=(), editable=False):
        super().__init__(parent)
        self.values = list(values)
        self.editable = editable
        self.rows = []  # (row_frame, combobox)
        self.add_row()

    def add_row(self, extra=False):
        row_frame = ttk.Frame(self)
        row_frame.pack(fill="x", pady=3)

        combobox = add_clear_button(ttk.Combobox(
            row_frame, values=self.values, state="normal" if self.editable else "readonly", width=40
        ))
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

            if not self.editable and combobox.get() not in self.values:
                combobox.set("")

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


def add_section(form, row, title):
    """A bold heading with a thin line under it."""
    section = ttk.Frame(form)
    section.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(22, 6))
    ttk.Label(section, text=title, style="Section.TLabel").pack(anchor="w")
    ttk.Separator(section).pack(fill="x", pady=(4, 0))


def add_field(form, row, label, widget, top=False, narrow=False):
    """Place "label  widget" on one row of the form and return the widget."""
    ttk.Label(form, text=label).grid(
        row=row, column=0, padx=(0, 18), pady=6, sticky="nw" if top else "w"
    )
    if isinstance(widget, (ttk.Entry, ttk.Combobox)):
        add_clear_button(widget)

    widget.grid(row=row, column=1, pady=6, sticky="w" if narrow else "ew")
    return widget


class SortableTable(ttk.Frame):
    """A table; clicking a column heading sorts by it (again: reverses). Empty cells always go last.

    columns is {key: (heading, width)}; the first column is the row id. numeric lists the columns
    that are sorted as numbers. on_double_click is called when a row is double-clicked.
    With count_label (for example "Books") the number of rows is shown under the table.
    """

    def __init__(self, parent, columns, numeric=(), sort_column=None, on_double_click=None, count_label=None):
        super().__init__(parent)
        self.columns = columns
        self.numeric = numeric
        self.rows = []
        self.sort = {"column": sort_column or next(iter(columns)), "descending": False}

        self.tree = ttk.Treeview(self, columns=list(columns), show="headings", selectmode="browse")

        for column, (heading, width) in columns.items():
            self.tree.heading(column, text=heading, anchor="w", command=lambda column=column: self.sort_by(column))
            self.tree.column(column, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.count_label = count_label
        self.count = ttk.Label(self, style="Muted.TLabel")

        if count_label:
            self.count.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        if on_double_click:
            self.tree.bind(
                "<Double-1>",
                lambda event: on_double_click() if self.tree.identify_region(event.x, event.y) == "cell" else None,
            )

    def set_rows(self, rows):
        self.rows = [["" if value is None else value for value in row] for row in rows]
        if self.count_label:
            self.count.configure(text=f"{self.count_label}: {len(self.rows)}")

        self.show_rows()

    def selected(self):
        """Values of the selected row (the first one is the id), or None."""
        selection = self.tree.selection()
        return self.tree.item(selection[0], "values") if selection else None

    def sort_by(self, column):
        self.sort["descending"] = not self.sort["descending"] if self.sort["column"] == column else False
        self.sort["column"] = column
        self.show_rows()

    def show_rows(self):
        selected = self.selected()
        selected_id = selected[0] if selected else None

        index = list(self.columns).index(self.sort["column"])
        filled = [row for row in self.rows if row[index] != ""]
        empty = [row for row in self.rows if row[index] == ""]

        if self.sort["column"] in self.numeric:
            filled.sort(key=lambda row: int(row[index]), reverse=self.sort["descending"])
        else:
            filled.sort(key=lambda row: str(row[index]).casefold(), reverse=self.sort["descending"])

        self.tree.delete(*self.tree.get_children())

        for row in filled + empty:
            item = self.tree.insert("", "end", values=row)

            if str(row[0]) == selected_id:
                self.tree.selection_set(item)

        for column, (heading, _) in self.columns.items():
            arrow = ""

            if column == self.sort["column"]:
                arrow = "  \u25bc" if self.sort["descending"] else "  \u25b2"

            self.tree.heading(column, text=heading + arrow)


class BookForm(ttk.Frame):
    """The book form. Without book_id it adds a book; with book_id it edits that book.

    on_saved is called after a book was changed (the window with the form can close itself then).
    """

    def __init__(self, parent, db_path, book_id=None, on_saved=None):
        super().__init__(parent, padding=(30, 20, 30, 20))
        self.db_path = db_path
        self.book_id = book_id
        self.on_saved = on_saved

        # label shown in the dropdown -> what add_new_book expects for that author
        self.author_choices = {}
        # authors typed in "New author" that are saved together with the book
        self.pending_authors = {}
        # names in another language for existing authors, saved together with the book: author_id -> {"name", "language"}
        self.pending_names = {}

        self.author_labels = {}     # author_id -> label in the dropdown
        self.author_languages = {}  # author_id -> languages the author already has a name in

        self.build_form()
        self.load_lists()

        if book_id is not None:
            self.fill_from_book()

    # -------------------------
    # Form
    # -------------------------

    def build_form(self):
        form = self
        form.columnconfigure(1, weight=1)

        rows = itertools.count()

        ttk.Label(form, text="Edit book" if self.book_id else "Add book", style="Title.TLabel").grid(
            row=next(rows), column=0, columnspan=2, sticky="w"
        )

        # Book
        add_section(form, next(rows), "Book")
        self.title_entry = add_field(form, next(rows), "Title", ttk.Entry(form))

        self.author_list = ChoiceList(form)
        add_field(form, next(rows), "Authors", self.author_list, top=True)

        author_buttons = ttk.Frame(form)
        author_buttons.grid(row=next(rows), column=1, sticky="w", pady=(2, 0))
        ttk.Button(author_buttons, text="Add new author", style="Small.TButton",
                   command=self.open_new_author).pack(side="left")
        ttk.Button(author_buttons, text="Add name to author", style="Small.TButton",
                   command=self.open_add_author_name).pack(side="left", padx=6)

        self.pending_note = ttk.Label(form, style="Muted.TLabel", justify="left", wraplength=380)
        self.pending_note.grid(row=next(rows), column=1, sticky="w")
        self.pending_note.grid_remove()

        # Edition
        add_section(form, next(rows), "Edition")
        self.publisher_combobox = add_field(
            form, next(rows), "Publisher", ttk.Combobox(form, values=PUBLISHERS)
        )
        self.language_combobox = add_field(
            form, next(rows), "Language", ttk.Combobox(form, values=LANGUAGES, state="readonly")
        )
        self.series_combobox = add_field(form, next(rows), "Series", ttk.Combobox(form))
        digits_only = (self.register(lambda text: text == "" or (text.isascii() and text.isdigit())), "%P")
        self.volume_entry = add_field(
            form, next(rows), "Volume number",
            ttk.Entry(form, width=8, validate="key", validatecommand=digits_only),
            narrow=True,
        )

        # Genres
        add_section(form, next(rows), "Genres")
        self.genre_list = ChoiceList(form, editable=True)
        add_field(form, next(rows), "Genres", self.genre_list, top=True)

        # Actions
        actions = ttk.Frame(form)
        actions.grid(row=next(rows), column=0, columnspan=2, sticky="ew", pady=(28, 0))
        ttk.Button(
            actions, text="Save changes" if self.book_id else "Save book",
            style="Accent.TButton", command=self.save_book,
        ).pack(side="left")
        self.actions = actions  # the window that shows the form may add its own buttons here

    def load_lists(self):
        """Refresh every dropdown from the database."""
        authors = library.list_authors(self.db_path)

        self.author_choices = {label: {"author_id": author_id} for author_id, label, _ in authors}
        self.author_labels = {author_id: label for author_id, label, _ in authors}
        self.author_languages = {author_id: languages.split(",") for author_id, _, languages in authors}
        self.author_choices.update(self.pending_authors)
        self.pending_names = {
            author_id: name for author_id, name in self.pending_names.items() if author_id in self.author_labels
        }
        self.author_list.set_values(sorted(self.author_choices, key=str.casefold))

        self.publisher_combobox["values"] = publisher_values(self.db_path)
        self.series_combobox["values"] = library.list_series(self.db_path)

        self.genre_list.set_values(sorted(library.list_genres(self.db_path), key=str.casefold))

        self.update_pending_note()

    def fill_from_book(self):
        """Put the stored book into the fields (edit mode)."""
        book = library.read_book(self.book_id, self.db_path)

        if book is None:
            messagebox.showerror("Book not found", "This book no longer exists.", parent=self.winfo_toplevel())
            self.winfo_toplevel().destroy()
            return

        self.title_entry.insert(0, book["title"])

        for author_id in book["author_ids"]:
            self.author_list.select(self.author_labels[author_id])

        self.publisher_combobox.set(book["publisher"])
        self.language_combobox.set(book["language"])
        self.series_combobox.set(book["series_name"] or "")
        self.volume_entry.insert(0, "" if book["volume_number"] is None else book["volume_number"])

        for genre in book["genres"]:
            self.genre_list.select(genre)

    def update_pending_note(self):
        """Remind what will be saved with the book besides the book itself."""
        lines = [
            f"+ {name['name']} ({name['language']}) will be added to {self.author_labels[author_id]}"
            for author_id, name in self.pending_names.items()
        ]

        if lines:
            self.pending_note.configure(text="\n".join(lines))
            self.pending_note.grid()
        else:
            self.pending_note.grid_remove()

    def reset_form(self):
        self.title_entry.delete(0, tk.END)
        self.author_list.reset()
        self.publisher_combobox.set("")
        self.language_combobox.set("")
        self.series_combobox.set("")
        self.volume_entry.delete(0, tk.END)
        self.genre_list.reset()

        self.pending_authors.clear()
        self.pending_names.clear()
        self.load_lists()

    # -------------------------
    # Small dialogs
    # -------------------------

    def make_dialog(self, title):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(background=BG)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        body = ttk.Frame(dialog, padding=22)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        return dialog, body

    def open_new_author(self):
        dialog, body = self.make_dialog("New author")

        name_entry = add_field(body, 0, "Name:", ttk.Entry(body, width=30))
        country_combobox = add_field(
            body, 1, "Country:", ttk.Combobox(body, values=country_values(self.db_path), width=27)
        )
        language_combobox = add_field(
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
        existing = {
            label: choice["author_id"]
            for label, choice in self.author_choices.items()
            if "author_id" in choice
        }

        if not existing:
            messagebox.showinfo("No authors", "There are no saved authors yet.", parent=self.winfo_toplevel())
            return

        dialog, body = self.make_dialog("Add name to author")

        author_combobox = add_field(
            body, 0, "Author:", ttk.Combobox(body, values=list(existing), state="readonly", width=40)
        )
        name_entry = add_field(body, 1, "Name:", ttk.Entry(body, width=43))
        language_combobox = add_field(
            body, 2, "Name language:", ttk.Combobox(body, values=LANGUAGES, state="readonly", width=40)
        )

        def save():
            label = author_combobox.get()
            name = name_entry.get().strip()
            language = language_combobox.get()

            if not label or not name or not language:
                messagebox.showwarning("Empty field", "Please fill in all fields.", parent=dialog)
                return

            author_id = existing[label]

            if language in self.author_languages[author_id]:
                messagebox.showwarning(
                    "Could not add name", "This author already has a name in that language.", parent=dialog
                )
                return

            if author_id in self.pending_names:
                messagebox.showwarning(
                    "Could not add name", "A name for this author is already waiting to be saved.", parent=dialog
                )
                return

            # saved together with the book, not now
            self.pending_names[author_id] = {"name": name, "language": language}
            self.load_lists()

            if label not in self.author_list.selected():
                self.author_list.select(label)

            dialog.destroy()

        ttk.Button(body, text="Save", style="Accent.TButton", command=save).grid(
            row=3, column=0, columnspan=2, sticky="e", pady=(14, 0)
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
            messagebox.showwarning("Empty field", "Please enter a book title.", parent=self.winfo_toplevel())
            return

        if not language:
            messagebox.showwarning("Empty field", "Please select a language.", parent=self.winfo_toplevel())
            return

        if not publisher:
            messagebox.showwarning("Empty field", "Please enter a publisher.", parent=self.winfo_toplevel())
            return

        author_labels = self.author_list.selected()

        if not author_labels:
            messagebox.showwarning("No author", "Please select at least one author.", parent=self.winfo_toplevel())
            return

        authors = []

        for label in author_labels:
            author = dict(self.author_choices[label])

            if author.get("author_id") in self.pending_names:
                author.update(self.pending_names[author["author_id"]])

            authors.append(author)

        volume_number = None

        if volume_text:
            try:
                volume_number = int(volume_text)
            except ValueError:
                messagebox.showwarning("Invalid volume number", "Volume number must be a number.", parent=self.winfo_toplevel())
                return

        book = dict(
            title=title,
            language=language,
            authors=authors,
            genres=self.genre_list.selected(),
            publisher=publisher,
            series_name=series_name or None,
            volume_number=volume_number,
            db_path=self.db_path,
        )

        try:
            if self.book_id is None:
                book_id = library.add_new_book(**book)
            else:
                library.update_book(self.book_id, **book)
        except (ValueError, sqlite3.IntegrityError) as error:
            title = "Could not add book" if self.book_id is None else "Could not save changes"
            messagebox.showerror(title, str(error), parent=self.winfo_toplevel())
            return

        if self.book_id is None:
            messagebox.showinfo("Book added", f"Book added successfully.\nBook ID: {book_id}", parent=self.winfo_toplevel())
            self.reset_form()
        else:
            messagebox.showinfo("Book saved", "Changes saved.", parent=self.winfo_toplevel())

            if self.on_saved:
                self.on_saved()


class LibraryApp:
    """The main window: the add-book form plus the "Manage books" window."""

    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path

        root.bind_all("<Control-KeyPress>", on_ctrl_key)

        self.form = BookForm(root, db_path)
        self.form.pack(fill="both", expand=True)
        ttk.Button(self.form.actions, text="Manage books", command=self.open_manage_books).pack(side="left", padx=12)
        ttk.Button(self.form.actions, text="Manage authors", command=self.open_manage_authors).pack(side="left")

        ttk.Label(root, text=f"Database: {db_path.name}", style="Muted.TLabel").pack(anchor="w", padx=30, pady=(0, 18))

    # -------------------------
    # Manage books
    # -------------------------

    def make_window(self, title, geometry):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(geometry)
        window.configure(background=BG)

        buttons = ttk.Frame(window)
        buttons.pack(side="bottom", fill="x", padx=20, pady=16)

        return window, buttons

    def open_manage_books(self):
        window, buttons = self.make_window("Manage books", "1130x480")

        table = SortableTable(
            window,
            {
                "book_id": ("ID", 45),
                "title": ("Title", 270),
                "authors": ("Authors", 270),
                "series": ("Series", 150),
                "volume": ("Volume", 65),
                "language": ("Language", 70),
                "publisher": ("Publisher", 130),
            },
            numeric=("book_id", "volume"),
            sort_column="title",
            on_double_click=lambda: edit_selected(),
            count_label="Books",
        )
        table.pack(fill="both", expand=True, padx=20, pady=(20, 5))

        def refresh():
            table.set_rows(library.list_books(self.db_path))

        def selected_book():
            book = table.selected()

            if book is None:
                messagebox.showwarning("No book selected", "Please select a book first.", parent=window)

            return book

        def edit_selected():
            book = selected_book()

            if book is None:
                return

            edit_window = tk.Toplevel(window)
            edit_window.title("Edit book")
            edit_window.configure(background=BG)
            edit_window.transient(window)

            def saved():
                edit_window.destroy()
                refresh()
                self.form.load_lists()  # the edit may have added or removed authors, series and genres

            BookForm(edit_window, self.db_path, book_id=int(book[0]), on_saved=saved).pack(fill="both", expand=True)

            if edit_window.winfo_exists():  # the form closes the window itself if the book is gone
                edit_window.grab_set()

        def delete_selected():
            book = selected_book()

            if book is None:
                return

            book_id, title = book[:2]

            if not messagebox.askyesno(
                "Confirm deletion",
                f"Delete '{title}' (ID: {book_id})?\nThis action cannot be undone.",
                parent=window,
            ):
                return

            library.delete_book(int(book_id), db_path=self.db_path)

            refresh()
            self.form.load_lists()  # authors/series/genres of the deleted book may be gone too

        ttk.Button(buttons, text="Edit selected book", command=edit_selected).pack(side="left")
        ttk.Button(buttons, text="Delete selected book", style="Danger.TButton", command=delete_selected).pack(side="left", padx=10)
        ttk.Button(buttons, text="Refresh list", command=refresh).pack(side="left")

        refresh()

    # -------------------------
    # Manage authors (edit only: authors are created and removed together with books)
    # -------------------------

    def open_manage_authors(self):
        window, buttons = self.make_window("Manage authors", "760x420")

        table = SortableTable(
            window,
            {
                "author_id": ("ID", 45),
                "names": ("Names", 360),
                "country": ("Country", 150),
                "books": ("Books", 70),
            },
            numeric=("author_id", "books"),
            sort_column="names",
            on_double_click=lambda: edit_selected(),
            count_label="Authors",
        )
        table.pack(fill="both", expand=True, padx=20, pady=(20, 5))

        def refresh():
            table.set_rows(library.list_authors_overview(self.db_path))

        def edit_selected():
            author = table.selected()

            if author is None:
                messagebox.showwarning("No author selected", "Please select an author first.", parent=window)
                return

            self.open_edit_author(window, int(author[0]), on_saved=lambda: (refresh(), self.form.load_lists()))

        ttk.Button(buttons, text="Edit selected author", command=edit_selected).pack(side="left")
        ttk.Button(buttons, text="Refresh list", command=refresh).pack(side="left", padx=10)

        refresh()

    def open_edit_author(self, parent, author_id, on_saved):
        author = library.read_author(author_id, self.db_path)

        if author is None:
            messagebox.showerror("Author not found", "This author no longer exists.", parent=parent)
            return

        dialog = tk.Toplevel(parent)
        dialog.title("Edit author")
        dialog.configure(background=BG)
        dialog.transient(parent)

        body = ttk.Frame(dialog, padding=22)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        country_combobox = add_field(
            body, 0, "Country", ttk.Combobox(body, values=country_values(self.db_path), width=40)
        )
        country_combobox.set(author["country"] or "")

        name_entries = {}

        for row, (language, name) in enumerate(author["names"].items(), start=1):
            entry = add_field(body, row, f"Name ({language})", ttk.Entry(body, width=43))
            entry.insert(0, name)
            name_entries[language] = entry

        def save():
            try:
                library.update_author(
                    author_id,
                    country_combobox.get(),
                    {language: entry.get() for language, entry in name_entries.items()},
                    db_path=self.db_path,
                )
            except ValueError as error:
                messagebox.showerror("Could not save author", str(error), parent=dialog)
                return

            dialog.destroy()
            on_saved()

        ttk.Button(body, text="Save changes", style="Accent.TButton", command=save).grid(
            row=len(name_entries) + 1, column=0, columnspan=2, sticky="e", pady=(14, 0)
        )

        dialog.grab_set()


def schema_problem(db_path):
    """Return a message if db_path is not a database in the current schema, otherwise None."""
    if not db_path.exists():
        return f"Database file not found:\n{db_path}\n\nCreate it with: python -m scripts.seed_library"

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
