from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from .models import UserProfile
from .serializers import RegisterSerializer, TelegramChatIdSerializer


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


class SetTelegramChatIdAPIView(GenericAPIView):
    """
    Сохраняет telegram_chat_id в профиле пользователя.
    """
    serializer_class = TelegramChatIdSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *_args, **_kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile, _created = UserProfile.objects.get_or_create(user=request.user)
        profile.telegram_chat_id = serializer.validated_data["telegram_chat_id"]
        profile.save(update_fields=["telegram_chat_id"])

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
