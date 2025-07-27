from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Payment, User, Subscription
from materials.models import Course, Lesson
from .payment_service import create_stripe_product, create_stripe_price, create_stripe_checkout_session
from .serializers import PaymentSerializer, UserSerializer, UserRegistrationSerializer
from .filters import PaymentFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
import stripe
import logging

logger = logging.getLogger(__name__)

class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['date']  # Поля для сортировки
    ordering = ['-date']  # Сортировка по умолчанию (по убыванию даты)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Payment.objects.filter(user=self.request.user).select_related('user', 'course', 'lesson')
        return Payment.objects.none()

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        lesson_id = request.data.get("lesson")
        payment_method = request.data.get("payment_method")

        if not self.request.user.is_authenticated:
            return Response({"error": "Требуется авторизация"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if payment_method == "stripe":
            try:
                # Получаем валидированные данные
                validated_data = serializer.validated_data
                item = validated_data['course'] or validated_data['lesson']
                item_type = "course" if validated_data['course'] else "lesson"

                # Создаем продукт и цену в Stripe
                product_id = create_stripe_product(item.title)
                price_id = create_stripe_price(product_id, float(item.price))

                # Создаем сессию оплаты
                success_url = request.build_absolute_uri(
                    reverse('materials:course-detail' if item_type == "course" else 'materials:lesson-detail', kwargs={'pk': course_id or lesson_id})
                )
                cancel_url = success_url
                session_data = create_stripe_checkout_session(price_id, success_url, cancel_url)

                # Сохраняем платеж с данными Stripe
                payment = Payment.objects.create(
                    user=validated_data['user'],
                    course=validated_data['course'],
                    lesson=validated_data['lesson'],
                    amount=validated_data['amount'],
                    payment_method="stripe",
                    stripe_session_id=session_data["session_id"],
                    payment_url=session_data["url"]
                )

                # Создаем подписку для курса
#                if item_type == "course":
#                    Subscription.objects.create(user=validated_data['user'], course=validated_data['course'])

                logger.info(f"Платеж создан: ID={payment.id}, URL={payment.payment_url}")
                return Response({"payment_url": session_data["url"]}, status=status.HTTP_201_CREATED)

            except stripe.error.StripeError as e:
                logger.error(f"Ошибка Stripe: {str(e)}")
                return Response({"error": f"Ошибка платежной системы: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Общая ошибка: {str(e)}")
                return Response({"error": "Внутренняя ошибка сервера"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Для не-Stripe платежей используем стандартное поведение
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # Опционально: ограничить доступ, чтобы пользователь видел только свой профиль
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()  # Если не авторизован, возвращаем пустой queryset

class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()

class SubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user  # Получаем текущего пользователя из запроса
        course_id = request.data.get('course_id')  # Получаем ID курса из тела запроса
        course = get_object_or_404(Course, id=course_id)  # Получаем объект курса или 404

        # Проверяем наличие подписки
        subs_item = Subscription.objects.filter(user=user, course=course)
        if subs_item.exists():
            # Если подписка есть, удаляем её
            subs_item.delete()
            message = 'подписка удалена'
        else:
            # Если подписки нет, создаём её
            Subscription.objects.create(user=user, course=course)
            message = 'подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)