import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from notifications.services import send_telegram_message

logger = logging.getLogger("notifications")


@shared_task
def send_habits_reminders() -> int:
    """
    Периодическая Celery-задача напоминаний о привычках.

    Логика:
    - проверяется текущее время (по минутам)
    - учитывается периодичность (periodicity + last_notified_at)
    - отправляется Telegram-уведомление владельцу привычки
    - задача устойчива к ошибкам (одна ошибка не роняет всю задачу)
    """
    now = timezone.localtime()
    logger.info(
        "send_habits_reminders: started now=%s",
        now.strftime("%Y-%m-%d %H:%M:%S"),
    )

    habits = (
        Habit.objects
        .select_related("owner", "owner__profile", "related_habit")
        .filter(is_pleasant=False)
        .filter(owner__profile__telegram_chat_id__isnull=False)
    )

    logger.info("send_habits_reminders: habits_total=%s", habits.count())

    sent = 0
    skipped_by_time = 0
    skipped_by_periodicity = 0

    now_minutes = now.hour * 60 + now.minute

    for habit in habits:
        habit_minutes = habit.time.hour * 60 + habit.time.minute

        # 1) Проверка времени (по минутам)
        if habit_minutes != now_minutes:
            skipped_by_time += 1
            continue

        # 2) Проверка периодичности
        if habit.last_notified_at:
            next_allowed = habit.last_notified_at + timedelta(days=habit.periodicity)
            if now < next_allowed:
                skipped_by_periodicity += 1
                logger.info(
                    "send_habits_reminders: skip_by_periodicity habit_id=%s owner=%s next_allowed=%s",
                    habit.id,
                    habit.owner.username,
                    next_allowed.strftime("%Y-%m-%d %H:%M:%S"),
                )
                continue

        chat_id = habit.owner.profile.telegram_chat_id

        # 3) Текст напоминания
        reward_text = ""
        if habit.related_habit:
            reward_text = f"\nНаграда: {habit.related_habit.action}"
        elif habit.reward:
            reward_text = f"\nНаграда: {habit.reward}"

        message = (
            f"⏰ Напоминание о привычке\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time.strftime('%H:%M')}"
            f"{reward_text}"
        )

        try:
            send_telegram_message(chat_id, message)
            habit.last_notified_at = now
            habit.save(update_fields=["last_notified_at"])
            sent += 1

            logger.info(
                "send_habits_reminders: sent habit_id=%s owner=%s",
                habit.id,
                habit.owner.username,
            )
        except Exception:  # noqa
            # Намеренно не роняем всю периодическую задачу из-за одной ошибки
            logger.exception(
                "send_habits_reminders: failed habit_id=%s owner=%s",
                habit.id,
                habit.owner.username,
            )

    logger.info(
        "send_habits_reminders: finished sent=%s skipped_by_time=%s skipped_by_periodicity=%s",
        sent,
        skipped_by_time,
        skipped_by_periodicity,
    )
    return sent
