from src.library_service import add_new_book


books = [
    {
        "title": "Тревожные люди",
        "language": "ru",
        "author_name": "Фредерик Бакман",
        "author_country": "Sweden",
        "publisher": "Синдбад",
    },
    {
        "title": "My Friends",
        "language": "en",
        "author_name": "Fredrik Backman",
        "author_country": "Sweden",
        "publisher": "Simon & Schuster",
    },
    {
        "title": "Marťan",
        "language": "cs",
        "author_name": "Andy Weir",
        "author_country": "United States",
        "publisher": "Laser",
    },
    {
        "title": "Элантрис",
        "language": "ru",
        "author_name": "Брендон Сандерсон",
        "author_country": "United States",
        "publisher": "Азбука",
    },
    {
        "title": "Локон с изумрудного моря",
        "language": "ru",
        "author_name": "Брендон Сандерсон",
        "author_country": "United States",
        "publisher": "Азбука",
    },
    {
        "title": "Озаренный Солнцем",
        "language": "ru",
        "author_name": "Брендон Сандерсон",
        "author_country": "United States",
        "publisher": "Азбука",
    },
    {
        "title": "Юми и укротитель кошмаров",
        "language": "ru",
        "author_name": "Брендон Сандерсон",
        "author_country": "United States",
        "publisher": "Азбука",
    },
    {
        "title": "Ученик убийцы. Королевский убийца",
        "language": "ru",
        "author_name": "Робин Хобб",
        "author_country": "United States",
        "publisher": "Азбука",
        "series_name": "Сага о Видящих",
        "volume_number": 1
    },
    {
        "title": "Странствия убийцы",
        "language": "ru",
        "author_name": "Робин Хобб",
        "author_country": "United States",
        "publisher": "Азбука",
        "series_name": "Сага о Видящих",
        "volume_number": 2
    },
    {
        "title": "The Wilful Princess and the Piebald Prince",
        "language": "en",
        "author_name": "Robin Hobb",
        "author_country": "United States",
        "publisher": "HarperCollins"
    },
    {
        "title": "Тайная история",
        "language": "ru",
        "author_name": "Донна Тартт",
        "author_country": "United States",
        "publisher": "Corpus",
    },
    {
        "title": "Alias Grace",
        "language": "cs",
        "author_name": "Margaret Atwood",
        "author_country": "Canada",
        "publisher": "Argo",
    },
    {
        "title": "Příběh služebnice",
        "language": "cs",
        "author_name": "Margaret Atwood",
        "author_country": "Canada",
        "publisher": "Argo",
    },
    {
        "title": "Svědectví",
        "language": "cs",
        "author_name": "Margaret Atwood",
        "author_country": "Canada",
        "publisher": "Argo",
    },
    {
        "title": "Замок Броуди",
        "language": "ru",
        "author_name": "Арчибальд Кронин",
        "author_country": "Scotland",
        "publisher": "Иностранка",
    },
    {
        "title": "Пробуждение Левиафана",
        "language": "ru",
        "author_name": "Джеймс Кори",
        "author_country": "United States",
        "publisher": "Азбука",
        "series_name": "Пространство",
        "volume_number": 1
    },
    {
        "title": "Война Калибана",
        "language": "ru",
        "author_name": "Джеймс Кори",
        "author_country": "United States",
        "publisher": "Азбука",
        "series_name": "Пространство",
        "volume_number": 2
    },
    {
        "title": "Врата Абаддона",
        "language": "ru",
        "author_name": "Джеймс Кори",
        "author_country": "United States",
        "publisher": "Азбука",
        "series_name": "Пространство",
        "volume_number": 3
    },

]

for book in books:
    add_new_book(**book)