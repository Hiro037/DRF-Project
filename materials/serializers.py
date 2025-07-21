from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from materials.models import Course, Lesson

from materials.validators import NoExternalLinksValidator
from users.models import Subscription


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [NoExternalLinksValidator()]

class CourseSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    is_subscribed = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_count_lessons_in_course(self, course):
        return Lesson.objects.filter(course=course).count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user  # Получаем текущего пользователя из контекста
        if user.is_authenticated:  # Проверяем, авторизован ли пользователь
            return Subscription.objects.filter(user=user, course=obj).exists()
        return False  # Неавторизованные пользователи не подписаны

    class Meta:
        model = Course
        fields = [
            'id',
            'count_lessons_in_course',
            'lessons',
            'title',
            'image',
            'description',
            'is_subscribed',
        ]
        validators = [NoExternalLinksValidator()]
