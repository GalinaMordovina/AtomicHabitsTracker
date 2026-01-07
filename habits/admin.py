from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Настройка отображения привычек в админке.
    Нужна для удобной проверки данных руками во время разработки.
    """

    list_display = (
        "id",
        "owner",
        "action",
        "time",
        "place",
        "is_pleasant",
        "related_habit",
        "periodicity",
        "reward",
        "duration",
        "is_public",
    )
    list_filter = ("is_pleasant", "is_public", "periodicity")
    search_fields = ("action", "place", "reward", "owner__username")
