from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def create(self, validated_data):
        # Создаём пользователя и правильно хэшируем пароль
        user = User(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class TelegramChatIdSerializer(serializers.Serializer):
    """
    Сериализатор для сохранения telegram_chat_id в профиле пользователя.
    """
    telegram_chat_id = serializers.CharField(max_length=64)
