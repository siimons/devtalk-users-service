# User Service - Dev Talk

## Описание

**dt-users** — это микросервис для управления пользователями в платформе **Dev Talk**. Данный микросервис отвечает за регистрацию, авторизацию, получение информации о пользователях, а также за их удаление. Сервис разработан на базе FastAPI и использует MySQL в качестве базы данных. Взаимодействие с другими микросервисами происходит через Kafka.

## Файловая структура микросервиса

```
dev-talk-users/
|
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── exceptions.py
│   │   │   ├── schemas.py
│   │   │   ├── views.py
│   │   │   ├── crud.py
│   │   │   └── services.py
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── cache_service.py
│   │   │   └── cache_exceptions.py
│   │   └── common/
│   │       ├── __init__.py
│   │       └── utils.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── database.py
│   └── events/
│       ├── __init__.py
│       ├── producer.py
│       └── consumer.py
|
├── migrations/
│   ├── __init__.py
│   └── models.sql
|
├── tests/
│   ├── unit/
│   │   ├── test_users.py
│   │   └── test_database.py
│   └── integration/
│       ├── test_endpoints.py
│       └── test_kafka.py
|
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```

## Функциональность

### CRUD

- POST `/api/v1/users` — создание нового пользователя.
- POST `/api/v1/auth/login` — вход пользователя в систему (аутентификация).
- GET `/api/v1/users/{user_id}` — получение информации о пользователе по его ID.
- PUT `/api/v1/users/{user_id}` — обновление информации о пользователе.
- DELETE `/api/v1/users/{user_id}` — удаление пользователя.
