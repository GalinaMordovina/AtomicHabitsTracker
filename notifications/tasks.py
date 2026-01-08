from celery import shared_task
from django.contrib.auth import get_user_model
import logging

from notifications.services import send_telegram_message

logger = logging.getLogger("notifications")
User = get_user_model()


@shared_task
def ping():
    logger.info("Celery ping: всё работает")
    return "pong"


@shared_task
def send_test_reminders():
    """
    Тестовая периодическая задача:
    отправляет сообщение всем пользователям, у кого есть telegram_chat_id.
    Нужна, чтобы проверить связку Celery -> Django -> Telegram.
    """

    logger.info("send_test_reminders: started")
    users = User.objects.select_related("profile").all()
    logger.info("send_test_reminders: users_count=%s", users.count())

    sent = 0

    for user in users:
        chat_id = getattr(getattr(user, "profile", None), "telegram_chat_id", None)
        logger.info("send_test_reminders: user=%s chat_id=%s", user.username, chat_id)

        if not chat_id:
            continue

        try:
            send_telegram_message(chat_id, "Тестовое напоминание из Celery")
            sent += 1
            logger.info("send_test_reminders: sent_to=%s", user.username)
        except Exception:
            # Не роняем всю задачу из-за одной ошибки
            logger.exception("send_test_reminders: failed_to_send user=%s", user.username)

    logger.info("send_test_reminders: finished sent=%s", sent)
    return sent
