from rest_framework.routers import SimpleRouter
from django.urls import path, include

from materials.apps import MaterialsConfig
from materials.views import CourseViewSet, LessonViewSet

router = SimpleRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')


app_name = MaterialsConfig.name

urlpatterns = [
    path('', include(router.urls)),  # Подключаем все маршруты из роутера
]
