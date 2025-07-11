from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView

from materials.models import Course, Lesson

from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        # чтение и обновление — модераторы или владельцы
        if self.action in ["retrieve", "update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        # создание и удаление — все авторизованные, кроме модераторов
        elif self.action in ["create", "destroy"]:
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        # list — любой авторизованный
        else:  # action == "list"
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        # при создании всегда ставим owner
        serializer.save(owner=self.request.user)

class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ["create", "destroy"]:
            if self.action == "create":
                self.permission_classes = [IsAuthenticated, ~IsModerator]
            else:  # destroy
                self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # list
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
