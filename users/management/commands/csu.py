from django.core.management import BaseCommand

from users.models import User


# Команда создает суперпользователя
class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User(email="superuser@example.com")
        user.set_password("qwerty")
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()