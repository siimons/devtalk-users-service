## Файловая структура проекта

```
articols
├── alembic/ # Для миграции базы данных
├── src # Основные файлы
│   ├── auth
│   │   ├── router.py # роуты
│   │   ├── schemas.py  # pydantic models (для запросов)
│   │   ├── models.py  # db models
│   │   ├── dependencies.py # скорее всего не нужно будет
│   │   ├── config.py  # local configs
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py # бизнес-логика
│   │   └── utils.py # функции для работы
│   ├── articles
│   │   ├── router.py  
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   └── comments
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py  # global configs
│   ├── models.py  # global models
│   ├── exceptions.py  # global exceptions
│   ├── pagination.py  # global module e.g. pagination
│   ├── database.py  # db connection related stuff
│   └── main.py
├── tests/
│   ├── auth
│   ├── articles
│   └── comments
├── templates/
│   └── index.html
├── requirements
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env
├── .gitignore
├── logging.ini
└── alembic.ini
```



## CRUD

Нужно создать ручки с помощью FastAPI.

### Статьи

- POST `/api/article/` - Создание статьи

- PUT `/api/article/{id}` - Изменение статьи

- DELETE `/api/article/{id}` - Удаление статьи

- GET `/api/articles/` - Получить все id статей

- GET `/api/article/{article_id}` - Получить какую-то отдельную статью (пригождается редко)

### Теги

Начинаются с символа #. На одной статье может быть не больше шести

- GET `/api/tags/{article_id}`

```json
[
    {
        "id": "1241293",
        "tags": "C++, ML"
    }
]
```

- POST `/api/tags/` - На вход подаём список с тегами. На Backend'e проверяем, есть ли тег в базе. Если есть, не добавляем

### Комментарии

- GET `/api/comments/{article_id}`