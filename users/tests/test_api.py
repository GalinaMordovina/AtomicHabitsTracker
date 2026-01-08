import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_register_creates_user():
    client = APIClient()

    payload = {"username": "testuser_api", "password": "testpass123"}
    resp = client.post("/api/users/register/", payload, format="json")

    assert resp.status_code == 201
    assert User.objects.filter(username="testuser_api").exists()


@pytest.mark.django_db
def test_set_telegram_chat_id_requires_auth():
    client = APIClient()

    resp = client.patch("/api/users/telegram/", {"telegram_chat_id": "123"}, format="json")

    # DRF обычно отдаёт 401 Unauthorized без токена
    assert resp.status_code == 401


@pytest.mark.django_db
def test_set_telegram_chat_id_success():
    client = APIClient()

    user = User.objects.create_user(username="tg_user", password="pass12345")
    client.force_authenticate(user=user)

    resp = client.patch("/api/users/telegram/", {"telegram_chat_id": "213259069"}, format="json")

    assert resp.status_code == 200
    user.refresh_from_db()

    # Профиль должен создаться автоматически через get_or_create в view
    assert user.profile.telegram_chat_id == "213259069"
