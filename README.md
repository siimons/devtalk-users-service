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
│   │   │   └── memcached_manager.py
│   │   └── common/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── hashing.py
│   │       └── jwt_manager.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── dependencies.py
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
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_services.py
│   │   ├── test_database.py
│   │   ├── test_cache.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── test_register_user.py
│   │   │   ├── test_get_user.py
│   │   │   ├── test_update_user.py
│   │   │   ├── test_delete_user.py
│   │   │   └── test_list_users.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── test_kafka_producer.py
│   │       └── test_kafka_consumer.py
│   └── e2e/
│       ├── __init__.py
│       └── test_user_flow.py
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

- POST `/api/v1/auth/register` — регистрация нового пользователя.
- POST `/api/v1/auth/login` — аутентификация пользователя, получение `access` и `refresh` токенов.
- POST `/api/v1/auth/logout` — выход пользователя из системы.
- GET `/api/v1/users/current` — получить данные текущего пользователя.
- PUT `/api/v1/users/current` — обновить данные текущего пользователя.
- DELETE `/api/v1/users/current` — удалить свой аккаунт.
