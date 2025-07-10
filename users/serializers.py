from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import Payment, User
from materials.models import Course, Lesson

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Выводим email пользователя
    course = serializers.StringRelatedField()  # Выводим название курса
    lesson = serializers.StringRelatedField()  # Выводим название урока

    class Meta:
        model = Payment
        fields = ['id', 'user', 'date', 'course', 'lesson', 'amount', 'payment_method']
        

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
