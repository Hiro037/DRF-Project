from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentViewSet


app_name = UsersConfig.name

# Создаём роутер для автоматической генерации URL
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')  # Эндпоинт для списка платежей
router.register(r'users', UserViewSet, basename='user')  # Эндпоинт для профиля пользователя

# Объединяем все маршруты
urlpatterns = [
    path('', include(router.urls)),  # Подключаем все маршруты из роутера
]