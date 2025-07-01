from rest_framework.routers import SimpleRouter
from django.urls import path

from materials.apps import MaterialsConfig
from materials.views import CourseViewSet, LessonListAPIView, LessonCreateAPIView, LessonUpdateAPIView, LessonDestroyAPIView, LessonRetrieveAPIView

router = SimpleRouter()
router.register('', CourseViewSet)

app_name = MaterialsConfig.name

urlpatterns = [
    path('lessons/', LessonListAPIView.as_view(), name='lesson_list'),
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson_retrieve'),
    path('lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson_delete'),
    path('lessons/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson_update'),
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson_create'),
]

urlpatterns += router.urls