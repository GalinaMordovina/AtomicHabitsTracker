from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Habit
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD для привычек пользователя.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пользователь должен видеть только свои привычки
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Автоматически подставляем владельца привычки
        serializer.save(owner=self.request.user)
