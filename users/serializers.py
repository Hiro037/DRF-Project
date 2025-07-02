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