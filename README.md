# Проект с Docker Compose

## Описание

Проект содержит следующие сервисы (с названиями на уровне `docker-compose`):

- `web` — backend (выполняет миграции и запускает сервер: `python manage.py migrate && python manage.py runserver 0.0.0.0:8000`)
- `db` — PostgreSQL
- `redis` — Redis (брокер/кеш)
- `celery` — Celery worker
- `celery-beat` — Celery Beat (планировщик)

Конфигурация сервисов берётся из файла `.env` (подключается через `env_file: - .env`).

Файл `docker-compose.yml` использует формат `version: "3.9"` и собирает образы из текущей директории (`build: .`).

## Требования

- Docker >= 20.10
- Docker Compose (или Docker Compose v2) — поддержка формата `3.9`

## Запуск проекта

1. Скопируйте шаблон `.env.example` в корне проекта в файл `.env` и заполните значения переменных (логины/пароли/ключи). Файл `.env` **не должен** попадать в репозиторий.

2. Соберите и запустите контейнеры:

```bash
docker-compose up --build
```

3. После успешного запуска сервисы будут доступны так:

- **Backend (web):** [http://localhost:8000](http://localhost:8000) (маппинг портов `8000:8000` в `docker-compose.yml`)
- **PostgreSQL (db):** доступен на `localhost:5432` (маппинг `5432:5432`)
- **Redis:** доступен на `localhost:6379` (маппинг `6379:6379`)

## Проверка работы сервисов

- **Backend:**
  - В браузере откройте `http://localhost:8000` или выполните:
    ```bash
    curl http://localhost:8000
    ```
  - Логи backend можно смотреть через:
    ```bash
    docker-compose logs -f web
    ```

- **PostgreSQL:**
  - Подключиться к psql с хоста:
    ```bash
    psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB
    ```
  - Либо через контейнер:
    ```bash
    docker-compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB
    ```

- **Redis:**
  - Локально:
    ```bash
    redis-cli -h localhost -p 6379 ping
    ```
  - Через контейнер:
    ```bash
    docker-compose exec redis redis-cli ping
    ```

- **Celery (worker):**
  - Просмотреть логи:
    ```bash
    docker-compose logs -f celery
    ```

- **Celery Beat (scheduler):**
  - Просмотреть логи:
    ```bash
    docker-compose logs -f celery-beat
    ```

## Документация API
- Swagger: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Остановка и очистка

- Остановка:
```bash
docker-compose down
```

- Остановка с удалением томов и промежуточных данных:
```bash
docker-compose down -v --remove-orphans
```

## Примечания по сервисам и окружению

- В `docker-compose.yml` переменные подключены через `env_file: - .env`. Убедитесь, что в `.env` заданы переменные для подключения к базе данных (например, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` или их аналоги, используемые в вашем проекте) и другие необходимые переменные.
- Сервис `web` выполняет миграции перед запуском сервера, что упрощает первый старт проекта.


