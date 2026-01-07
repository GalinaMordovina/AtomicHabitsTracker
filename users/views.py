from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer


class RegisterAPIView(generics.CreateAPIView):
    """
    Регистрация пользователя.

    Доступ:
    - AllowAny, потому что новый пользователь ещё не может иметь токен.

    Что делает:
    - принимает username и password
    - создаёт пользователя
    - возвращает созданного пользователя (без пароля)
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
