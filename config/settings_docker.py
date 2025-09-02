from .settings import *  # Импортируем все из основных настроек

# Переопределяем ВСЕ настройки, которые должны быть специфичны для Docker-окружения
# Это настройки, которые используют имена сервисов вместо localhost

# База данных: используем сервис 'db'
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": "db",  # <- Имя сервиса в Docker Compose
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}

# Celery: используем сервис 'redis'
CELERY_BROKER_URL = 'redis://redis:6379/0'  # <- Имя сервиса в Docker Compose
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'  # <- Имя сервиса в Docker Compose

# Кеш: используем сервис 'redis'
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/1",  # <- Имя сервиса в Docker Compose
    }
}

# DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Можно также указать ALLOWED_HOSTS для принятия запросов от nginx и др.
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web']  # 'web' - имя сервиса внутри сети
ALLOWED_HOSTS = ['*']

# Настройки для статики, если обслуживаетесь через nginx в другом контейнере
# STATIC_URL = '/static/'
# STATIC_ROOT = '/app/staticfiles'  # Должно совпадать с томом в nginx
# MEDIA_URL = '/media/'
# MEDIA_ROOT = '/app/media'  # Должно совпадать с томом в nginx