from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPagination
from .permissions import IsOwnerOrReadOnly


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD для привычек пользователя.
    Пользователь видит и изменяет только свои привычки.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = HabitPagination

    def get_queryset(self):
        # Пользователь должен видеть только свои привычки
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Автоматически подставляем владельца привычки
        serializer.save(owner=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Список публичных привычек.
    Доступен всем авторизованным пользователям, только чтение.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
