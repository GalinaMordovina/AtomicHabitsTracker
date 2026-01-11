from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    Профиль пользователя.

    Зачем:
    - модель User трогать не обязательно
    - сюда удобно добавлять настройки (например chat_id для Telegram)
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )

    telegram_chat_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Telegram chat_id",
        help_text="Идентификатор чата пользователя в Telegram для отправки напоминаний.",
    )

    def __str__(self) -> str:
        return f"Profile({self.user})"


# ВАЖНО:
# Импорт сигналов должен быть в самом конце файла,
# чтобы модели были полностью загружены (+ заглушечка)
from . import signals  # noqa: F401
