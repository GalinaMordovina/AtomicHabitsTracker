from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор привычки.

    Здесь мы реализуем бизнес-валидацию:
    - проверяем связку reward/related_habit
    - ограничиваем duration
    - проверяем, что related_habit только приятная
    - запрещаем reward/related_habit для приятных привычек
    - ограничиваем periodicity (не реже 1 раза в 7 дней)
    """

    class Meta:
        model = Habit
        fields = (
            "id",
            "owner",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "created_at", "updated_at")

    def validate(self, attrs):
        """
        Объектная валидация: проверяем сразу несколько полей,
        потому что условия зависят от комбинаций.
        """
        # При обновлении часть полей может не прийти, поэтому подставляем текущие значения из instance.
        is_pleasant = attrs.get("is_pleasant", getattr(self.instance, "is_pleasant", False))
        related_habit = attrs.get("related_habit", getattr(self.instance, "related_habit", None))
        reward = attrs.get("reward", getattr(self.instance, "reward", None))
        duration = attrs.get("duration", getattr(self.instance, "duration", None))
        periodicity = attrs.get("periodicity", getattr(self.instance, "periodicity", 1))

        # 1) Нельзя одновременно reward и related_habit
        if reward and related_habit:
            raise serializers.ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку."
            )

        # 2) Время выполнения не больше 120 секунд
        if duration is not None and duration > 120:
            raise serializers.ValidationError(
                "Время выполнения привычки не должно превышать 120 секунд."
            )

        # 5) Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if periodicity is not None and periodicity > 7:
            raise serializers.ValidationError(
                "Нельзя устанавливать периодичность реже, чем 1 раз в 7 дней."
            )

        # 3) В связанные привычки могут попадать только приятные привычки
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "Связанная привычка должна быть приятной (is_pleasant=True)."
            )

        # 4) У приятной привычки не может быть reward или related_habit
        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        return attrs
