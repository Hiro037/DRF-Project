# Проект с Docker Compose

## Описание

Проект представляет собой Django-приложение с использованием Docker Compose. Включает следующие сервисы (с названиями на уровне `docker-compose`):

- `web` — backend (выполняет миграции и запускает сервер: `python manage.py migrate --settings=config.settings_docker && python manage.py runserver 0.0.0.0:8000 --settings=config.settings_docker`).
- `db` — PostgreSQL (версия 15).
- `redis` — Redis (версия 7, используется как брокер/кеш).
- `celery` — Celery worker.
- `celery-beat` — Celery Beat (планировщик задач).
- `nginx` — веб-сервер для обслуживания статических файлов и проксирования запросов к `web`.

Конфигурация сервисов берётся из файла `.env` (подключается через `env_file: - .env`). Файл `docker-compose.yml` использует формат `version: "3.9"` и собирает образы из текущей директории (`build: .`).

## Требования

- Docker >= 20.10
- Docker Compose (или Docker Compose v2) — поддержка формата `3.9`
- Python 3.12 (для CI/CD и локальной разработки)

## Запуск проекта

### Локальный запуск

1. Скопируйте шаблон `.env_example` в корне проекта в файл `.env` и заполните значения переменных (логины, пароли, ключи). Файл `.env` **не должен** попадать в репозиторий. Пример переменных:
   - `SECRET_KEY`
   - `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
   - `STRIPE_SECRET_KEY`
   - `EMAIL`, `EMAILPASSWORD`

2. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```

3. После успешного запуска сервисы будут доступны:
   - **Backend (web):** [http://localhost:8000](http://localhost:8000) (порт `8000:8000`).
   - **PostgreSQL (db):** `localhost:5432` (порт `5432:5432`).
   - **Redis:** `localhost:6379` (порт `6379:6379`).

### Проверка работы сервисов

- **Backend:**
  - Откройте в браузере [http://localhost:8000](http://localhost:8000) или выполните:
    ```bash
    curl http://localhost:8000
    ```
  - Логи backend:
    ```bash
    docker-compose logs -f web
    ```

- **PostgreSQL:**
  - Подключение с хоста:
    ```bash
    psql -h localhost -U $DATABASE_USER -d $DATABASE_NAME
    ```
  - Через контейнер:
    ```bash
    docker-compose exec db psql -U $DATABASE_USER -d $DATABASE_NAME
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
  - Логи:
    ```bash
    docker-compose logs -f celery
    ```

- **Celery Beat (scheduler):**
  - Логи:
    ```bash
    docker-compose logs -f celery-beat
    ```

- **Nginx:**
  - Проверьте доступ к статическим файлам и проксирование на [http://localhost:8000](http://localhost:8000).

### Документация API
- Swagger: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

### Остановка и очистка
- Остановка:
  ```bash
  docker-compose down
  ```
- Остановка с удалением томов и промежуточных данных:
  ```bash
  docker-compose down -v --remove-orphans
  ```

### Запуск на удалённом сервере

Приложение развёрнуто на публичном IP: [http://89.169.179.249](http://89.169.179.249). Для ручного деплоя на сервер (Ubuntu) выполните следующие шаги:

1. **Установите зависимости:**
   ```bash
   sudo apt update && sudo apt install python3 python3-venv python3-pip git nginx docker.io docker-compose -y
   ```

2. **Клонируйте проект:**
   Клонируйте репозиторий в выбранную директорию (например, `/var/www/myproject`):
   ```bash
   git clone <repository-url> /var/www/myproject
   cd /var/www/myproject
   ```

3. **Настройте окружение:**
   - Создайте файл `.env` на сервере на основе `.env_example`, заполнив все переменные (см. список выше).
   - Убедитесь, что доступны переменные окружения для базы данных и других сервисов.

4. **Настройте Nginx:**
   - Скопируйте `nginx.conf` в `/etc/nginx/conf.d/myproject.conf`:
     ```bash
     sudo cp nginx.conf /etc/nginx/conf.d/myproject.conf
     ```
   - Отредактируйте `server_name` в `nginx.conf` на ваш домен (например, `89.169.179.249`) или оставьте `localhost` для IP-доступа.
   - Перезапустите Nginx:
     ```bash
     sudo systemctl restart nginx
     ```

5. **Запустите Docker Compose:**
   ```bash
   sudo docker-compose up --build -d
   ```

6. **Выполните миграции и сбор статики:**
   ```bash
   sudo docker-compose exec web python manage.py migrate --noinput
   sudo docker-compose exec web python manage.py collectstatic --noinput
   ```

7. **Настройте firewall (опционально):**
   Откройте порты 80, 443, 22:
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw allow 22
   sudo ufw enable
   ```

## Примечания по сервисам и окружению

- В `docker-compose.yml` переменные подключены через `env_file: - .env`. Убедитесь, что в `.env` заданы `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD` и другие необходимые переменные.
- Сервис `web` выполняет миграции перед запуском сервера.
- Используются тома `static_volume` и `media_volume` для хранения статических файлов и медиа.

## 🚀 Деплой и CI/CD

### Настройка сервера

1. Установите зависимости (см. выше).
2. Клонируйте проект в `/var/www/myproject`.
3. Настройте Nginx (см. шаги выше).
4. Откройте порты 80, 443, 22, используйте SSH-ключи для доступа.

### Переменные окружения

В репозитории есть файл `.env_example`. На сервере создайте `.env` с рабочими значениями. В GitHub Actions секреты добавьте в **Settings → Secrets and variables → Actions**:
- `SSH_USER` — пользователь сервера.
- `SERVER_IP` — IP-адрес сервера (например, `89.169.179.249`).
- `SSH_KEY` — приватный ключ для доступа.
- `DEPLOY_DIR` — директория на сервере (например, `/var/www/myproject`).
- `SECRET_KEY`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `STRIPE_SECRET_KEY`, `EMAIL`, `PASSWORD` — секреты для приложения.

### CI/CD

Используется GitHub Actions (`.github/workflows/ci.yml`):
- При push в ветки `develop` или `homework-35-2` запускаются тесты (`python manage.py test --settings=config.settings_ci`).
- Если тесты успешны, выполняется деплой:
  - Синхронизация файлов через `rsync`.
  - Установка зависимостей через Poetry.
  - Миграции, сбор статики, перезапуск сервисов с бэкапом базы данных.
  - Переменные окружения создаются на сервере автоматически.

---