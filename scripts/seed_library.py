from src.library_service import add_new_book, create_genre


books = [
    {
        "title": "Тревожные люди",
        "language": "ru",
        "authors": [
            {
            "name": "Фредерик Бакман",
            "country": "Sweden"
            }
        ],
        "publisher": "Синдбад",
    },
    {
        "title": "My Friends",
        "language": "en",
        "authors": [
            {
            "name": "Fredrik Backman",
            "country": "Sweden"
            }
        ],
        "publisher": "Simon & Schuster",
    },
    {
        "title": "Marťan",
        "language": "cs",
        "authors": [
            {
            "name": "Andy Weir",
            "country": "United States"
            }
        ],
        "genres": ["Science Fiction"],
        "publisher": "Laser",
    },
    {
        "title": "Элантрис",
        "language": "ru",
        "authors": [
            {
            "name": "Брендон Сандерсон",
            "country": "United States"
            }
        ],
        "genres": ["Fantasy"],
        "publisher": "Азбука",
    },
    {
        "title": "Локон с изумрудного моря",
        "language": "ru",
        "authors": [
            {
            "name": "Брендон Сандерсон",
            "country": "United States"
            }
        ],
        "publisher": "Азбука",
    },
    {
        "title": "Озаренный Солнцем",
        "language": "ru",
        "authors": [
            {
            "name": "Брендон Сандерсон",
            "country": "United States"
            }
        ],
        "publisher": "Азбука",
    },
    {
        "title": "Юми и укротитель кошмаров",
        "language": "ru",
        "authors": [
            {
            "name": "Брендон Сандерсон",
            "country": "United States"
            }
        ],
        "publisher": "Азбука",
    },
    {
        "title": "Ученик убийцы. Королевский убийца",
        "language": "ru",
        "authors": [
            {
            "name": "Робин Хобб",
            "country": "United States"
            }
        ],
        "genres": ["Fantasy"],
        "publisher": "Азбука",
        "series_name": "Сага о Видящих",
        "volume_number": 1
    },
    {
        "title": "Странствия убийцы",
        "language": "ru",
        "authors": [
            {
            "name": "Робин Хобб",
            "country": "United States"
            }
        ],
        "genres": ["Fantasy"],
        "publisher": "Азбука",
        "series_name": "Сага о Видящих",
        "volume_number": 2
    },
    {
        "title": "The Wilful Princess and the Piebald Prince",
        "language": "en",
        "authors": [
            {
            "name": "Robin Hobb",
            "country": "United States"
            }
        ],
        "publisher": "HarperCollins"
    },
    {
        "title": "Тайная история",
        "language": "ru",
        "authors": [
            {
            "name": "Донна Тартт",
            "country": "United States"
            }
        ],
        "genres": ["Modern Prose", "Literary Fiction"],
        "publisher": "Corpus"
    },
    {
        "title": "Alias Grace",
        "language": "cs",
        "authors": [
            {
            "name": "Margaret Atwood",
            "country": "Canada"
            }
        ],
        "genres": ["Historical Fiction", "Literary Fiction"],
        "publisher": "Argo"
    },
    {
        "title": "Příběh služebnice",
        "language": "cs",
        "authors": [
            {
            "name": "Margaret Atwood",
            "country": "Canada"
            }
        ],
        "publisher": "Argo"
    },
    {
        "title": "Svědectví",
        "language": "cs",
        "authors": [
            {
            "name": "Margaret Atwood",
            "country": "Canada"
            }
        ],
        "publisher": "Argo"
    },
    {
        "title": "Замок Броуди",
        "language": "ru",
        "authors": [
            {
            "name": "Арчибальд Кронин",
            "country": "Scotland"
            }
        ],
        "genres": ["Classic Literature"],
        "publisher": "Иностранка"
    },
    {
        "title": "Пробуждение Левиафана",
        "language": "ru",
        "authors": [
            {
            "name": "Джеймс Кори",
            "country": "United States"
            }
        ],
        "genres": ["Science Fiction"],
        "publisher": "Азбука",
        "series_name": "Пространство",
        "volume_number": 1
    },
    {
        "title": "Война Калибана",
        "language": "ru",
        "authors": [
            {
            "name": "Джеймс Кори",
            "country": "United States"
            }
        ],
        "genres": ["Science Fiction"],
        "publisher": "Азбука",
        "series_name": "Пространство",
        "volume_number": 2
    },
    {
        "title": "Врата Абаддона",
        "language": "ru",
        "authors": [
            {
            "name": "Джеймс Кори",
            "country": "United States"
            }
        ],
        "genres": ["Science Fiction"],
        "publisher": "Азбука",
        "series_name": "Пространство",
        "volume_number": 3
    },
    {
        "title": "The Hunger Games",
        "language": "en",
        "authors": [
            {
            "name": "Suzanne Collins",
            "country": "United States"
            }
        ],
        "publisher": "Scholastic",
        "series_name": "The Hunger Games",
        "volume_number": 1
    },
    {
        "title": "Catching Fire",
        "language": "en",
        "authors": [
            {
            "name": "Suzanne Collins",
            "country": "United States"
            }
        ],
        "publisher": "Scholastic",
        "series_name": "The Hunger Games",
        "volume_number": 2
    },
    {
        "title": "Mockingjay",
        "language": "en",
        "authors": [
            {
            "name": "Suzanne Collins",
            "country": "United States"
            }
        ],
        "publisher": "Scholastic",
        "series_name": "The Hunger Games",
        "volume_number": 3
    },
    {
        "title": "The Ballad of Songbirds and Snakes",
        "language": "en",
        "authors": [
            {
            "name": "Suzanne Collins",
            "country": "United States"
            }
        ],
        "publisher": "Scholastic",
        "series_name": "The Hunger Games",
        "volume_number": None
    },
    {
        "title": "Град обреченный",
        "language": "ru",
        "authors": [
            {
            "name": "Аркадий Стругацкий",
            "country": "Russia"
            },
            {
            "name": "Борис Стругацкий",
            "country": "Russia"
            }
        ],
        "genres": ["Science Fiction", "Dystopian Fiction"],
        "publisher": "АСТ"
    },
    {
        "title": "Пикник на обочине",
        "language": "ru",
        "authors": [
            {
            "name": "Аркадий Стругацкий",
            "country": "Russia"
            },
            {
            "name": "Борис Стругацкий",
            "country": "Russia"
            }
        ],
        "publisher": "АСТ"
    },
    {
    "title": "Všechny jeho lži",
    "language": "cs",
    "authors": [
        {"name": "James Patterson", "country": "United States"}
    ],
    "genres": ["Thriller"],
    "publisher": "Alpress"
    }
]

genres = [
    "Classic Literature",
    "Dystopian Fiction",
    "Fantasy",
    "Historical Fiction",
    "Literary Fiction",
    "Modern Prose",
    "Mystery",
    "Romance",
    "Science Fiction",
    "Thriller",
    "Young Adult"
]


for genre in genres:
    create_genre(genre)

for book in books:
    add_new_book(**book)