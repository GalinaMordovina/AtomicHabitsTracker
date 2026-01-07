import os
import requests


class TelegramError(Exception):
    """Ошибка при отправке сообщения в Telegram."""


def send_telegram_message(chat_id: str, text: str) -> None:
    """
    Отправляет сообщение в Telegram через Bot API.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise TelegramError("Не задан TELEGRAM_BOT_TOKEN в окружении.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code != 200:
        raise TelegramError(f"Telegram API error: {resp.status_code} {resp.text}")
