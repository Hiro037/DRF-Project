import logging

from celery import shared_task
from .models import User
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def activity_check():
    try:
        # Получаем текущую дату и время с учетом часового пояса
        threshold = timezone.now() - timedelta(days=30)

        # Фильтруем пользователей, которые не входили более 30 дней
        inactive_users = User.objects.filter(last_login__lt=threshold)

        # Обновляем is_active
        count = inactive_users.update(is_active=False)

        # Логируем результат
        logger.info(f"Деактивировано {count} пользователей, которые не посещади сайт более 30 дней")

    except Exception as e:
        logger.error(f"Ошибка в задаче activity_check: {e}")
        raise