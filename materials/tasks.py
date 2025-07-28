from celery import shared_task
from config.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from users.models import User, Subscription


@shared_task
def mailing(instance):
    try:
        recipients = list(Subscription.objects.filter(course=instance).values_list('user__email', flat=True))
        if recipients:  # Проверка, что список не пустой
            send_mail(
                subject='Обновление курса!',
                message=f'Обновлен курс "{instance.title}"!',
                from_email=EMAIL_HOST_USER,
                recipient_list=recipients,
                fail_silently=False
            )
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")  # Логирование ошибки
