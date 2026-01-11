from django.conf import settings
from django.db import models


class Habit(models.Model):
    """
    Привычка пользователя.

    Модель покрывает оба типа привычек:
    - полезная привычка (is_pleasant=False) может иметь reward ИЛИ related_habit
    - приятная привычка (is_pleasant=True) - это "награда", у неё не бывает reward/related_habit
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
        help_text="Создатель привычки.",
    )

    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Где пользователь будет выполнять привычку (например: дома, парк, офис).",
    )

    time = models.TimeField(
        verbose_name="Время",
        help_text="Во сколько нужно выполнять привычку.",
    )

    action = models.CharField(
        max_length=255,
        verbose_name="Действие",
        help_text="Формулировка привычки: что именно нужно сделать.",
    )

    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Приятная привычка",
        help_text="Если True - это приятная привычка (награда), а не полезная.",
    )

    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_for",
        verbose_name="Связанная привычка",
        help_text="Приятная привычка-награда, которая выполняется после полезной.",
    )

    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность (дни)",
        help_text="Как часто выполнять привычку (в днях). По умолчанию ежедневно (1).",
    )

    reward = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Чем наградить себя после выполнения (если не используется связанная привычка).",
    )

    duration = models.PositiveSmallIntegerField(
        verbose_name="Время на выполнение (секунды)",
        help_text="Сколько секунд занимает выполнение. Должно быть не больше 120.",
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная",
        help_text="Если True - привычку видно в списке публичных привычек.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    last_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последняя отправка напоминания"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        # Для админки и логов удобно видеть короткое описание привычки
        return f"{self.owner} — {self.action} ({self.time})"
