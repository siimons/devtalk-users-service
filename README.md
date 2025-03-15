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
│   │   │   ├── repositories.py
│   │   │   └── services.py
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── redis.py
│   │   ├── common/
│   │   │   ├── __init__.py
│   │   │   ├── authentication.py
│   │   │   ├── hashing.py
│   │   │   ├── jwt_manager.py
│   │   │   └── tokens.py
│   │   └── security/
│   │       ├── __init__.py
│   │       ├── rate_limiter.py
│   │       └── exceptions.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── logging.py
│   │   └── dependencies/
│   │       ├── __init__.py
│   │       ├── repositories.py
│   │       ├── services.py
│   │       └── common.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── producer.py
│   │   └── consumer.py
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── email.py
│   │   ├── schemas.py
│   │   └── templates/
│   │       ├── restoration_token.html
│   │       └── welcome.html
│   └── workers/
│       ├── __init__.py
│       ├── celery.py
│       └── tasks/
│           ├── __init__.py
│           ├── send_email.py
│           └── delete_account.py
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
│   │   ├── test_storage_database.py
│   │   ├── test_storage_redis.py
│   │   └── test_notifications.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── test_get_user_endpoint.py
│   │   │   ├── test_login_user_endpoint.py
│   │   │   ├── test_logout_user_endpoint.py
│   │   │   ├── test_register_user_endpoint.py
│   │   │   └── test_update_user_endpoint.py
│   │   ├── events/
│   │   │   ├── __init__.py
│   │   │   ├── test_producer.py
│   │   │   └── test_consumer.py
│   │   └── workers/
│   │       ├── __init__.py
│   │       ├── test_workers_celery.py
│   │       └── test_tasks.py
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

#### Аутентификация и управление сессией

- POST `/api/v1/auth/register` — регистрация нового пользователя.
- POST `/api/v1/auth/login` — аутентификация пользователя, получение `access` и `refresh` токенов.
- POST `/api/v1/auth/logout` — выход пользователя из системы, удаление `access` и `refresh` токенов.

#### Управление профилем пользователя

- GET `/api/v1/users/current` — получить данные текущего пользователя.
- PATCH `/api/v1/users/current` — обновить данные текущего пользователя.
- DELETE `/api/v1/users/current` — удалить аккаунт текущего пользователя.
- POST `/api/v1/users/restore` – восстановить ранее удалённый аккаунт.
