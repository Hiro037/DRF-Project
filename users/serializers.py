from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from users.models import Payment, User
from materials.models import Course, Lesson

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['date', 'stripe_session_id', 'payment_url', 'user']

    def validate(self, data):
        payment_method = data.get('payment_method')
        course_id = self.context['request'].data.get('course_id')
        lesson_id = self.context['request'].data.get('lesson_id')

        # Проверяем, что указан либо курс, либо урок, но не оба
        if not course_id and not lesson_id:
            raise serializers.ValidationError("Укажите курс или урок")
        if course_id and lesson_id:
            raise serializers.ValidationError("Укажите только курс или урок, но не оба")

        # Проверяем, что объект существует и цена валидна
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            if course.price <= 0:
                raise serializers.ValidationError("Цена курса должна быть больше нуля")
            data['course'] = course
            data['lesson'] = None
            data['amount'] = course.price
        elif lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            if lesson.price <= 0:
                raise serializers.ValidationError("Цена урока должна быть больше нуля")
            data['lesson'] = lesson
            data['course'] = None
            data['amount'] = lesson.price

        # Для Stripe-платежей проверяем, что метод оплаты корректен
        if payment_method == 'stripe':
            if 'stripe_session_id' in data or 'payment_url' in data:
                raise serializers.ValidationError("Поля stripe_session_id и payment_url заполняются автоматически")
        else:
            # Для не-Stripe платежей сбрасываем поля Stripe
            data['stripe_session_id'] = None
            data['payment_url'] = None

        # Устанавливаем пользователя из запроса
        data['user'] = self.context['request'].user
        return data
        

class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source='payment_set')

    class Meta:
        model = User
        fields = ['id', 'email', 'pfp', 'phone_number', 'city', 'payments']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']  # убираем 'username'

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = User.objects.create_user(
            email=email,
            password=password
        )
        return user
