from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from materials.models import Course, Lesson

class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class CourseSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_count_lessons_in_course(self, course):
        return Lesson.objects.filter(course=course).count()

    class Meta:
        model = Course
        fields = [
            'id',
            'count_lessons_in_course',
            'lessons',
            'title',
            'image',
            'description',
        ]
