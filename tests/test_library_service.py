from src.library_service import add_new_book


book_id = add_new_book(
    title="Тревожные люди",
    language="ru",
    author_name="Фредерик Бакман",
    author_country="SWE",
    publisher="Синдбад",
)

print(book_id)