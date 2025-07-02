from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from users.models import Payment, User
from .serializers import PaymentSerializer, UserSerializer
from .filters import PaymentFilter

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['date']  # Поля для сортировки
    ordering = ['-date']  # Сортировка по умолчанию (по убыванию даты)

    def get_queryset(self):
        return Payment.objects.all().select_related('user', 'course', 'lesson')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # Опционально: ограничить доступ, чтобы пользователь видел только свой профиль
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()  # Если не авторизован, возвращаем пустой queryset