# 1. Базовый образ Python
FROM python:3.12-slim

# 2. Настройки Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Рабочая директория
WORKDIR /app

# 4. Устанавливаем зависимости системы (для psycopg2, Pillow и т.д.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Устанавливаем poetry
RUN pip install --no-cache-dir poetry

# 6. Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock ./

# 7. Устанавливаем зависимости (без виртуального окружения)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 8. Копируем проект
COPY . .

# 9. Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
