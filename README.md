# Example Server

Тестовое backend-приложение на FastAPI с PostgreSQL, ORM и миграциями.

## Stack

- FastAPI
- PostgreSQL
- ORM
- Alembic
- Docker
- Docker Compose
- Pytest

## Run

1. Создать `.env` на основе `.env.example`.
2. Собрать контейнеры:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml build
```

3. Запустить проект в фоне:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

4. Просмотр логов:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
```

После запуска будут доступны:

- API: `http://localhost:5142`
- OpenAPI / Swagger UI: `http://localhost:5142/docs`
- ReDoc: `http://localhost:5142/redoc`
- PostgreSQL: `localhost:5141`

## Stop

Остановить проект:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

Остановить проект и удалить volumes базы данных:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
```

Команду с `-v` стоит использовать только если нужно полностью сбросить локальные данные PostgreSQL.

## Development Mode

Локальная разработка запускается через `docker-compose.dev.yml`.
Backend работает в dev-режиме с автоперезагрузкой кода.
