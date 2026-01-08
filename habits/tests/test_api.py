import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from habits.models import Habit

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(api_client):
    u = User.objects.create_user(username="u1", password="pass12345")
    api_client.force_authenticate(user=u)
    return u


@pytest.fixture
def other_user():
    return User.objects.create_user(username="u2", password="pass12345")


@pytest.mark.django_db
def test_user_sees_only_own_habits(api_client, user, other_user):
    Habit.objects.create(
        owner=user,
        place="Дом",
        time="10:00",
        action="Читать книгу",
        is_pleasant=False,
        reward="Чай",
        duration=60,
        periodicity=1,
        is_public=False,
    )
    Habit.objects.create(
        owner=other_user,
        place="Парк",
        time="10:00",
        action="Гулять",
        is_pleasant=False,
        reward="Кофе",
        duration=60,
        periodicity=1,
        is_public=False,
    )

    resp = api_client.get("/api/habits/")
    assert resp.status_code == 200

    # DRF пагинация может вернуть либо список, либо dict с results
    data = resp.json()
    results = data.get("results", data)

    assert len(results) == 1
    assert results[0]["action"] == "Читать книгу"


@pytest.mark.django_db
def test_create_habit_duration_more_than_120_fails(api_client, user):
    payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Приседания",
        "is_pleasant": False,
        "reward": "Шоколад",
        "duration": 121,
        "periodicity": 1,
        "is_public": False,
    }

    resp = api_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_create_habit_periodicity_more_than_7_fails(api_client, user):
    payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Читать книгу",
        "is_pleasant": False,
        "reward": "Чай",
        "duration": 60,
        "periodicity": 8,
        "is_public": False,
    }

    resp = api_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_create_habit_reward_and_related_habit_together_fails(api_client, user):
    pleasant = Habit.objects.create(
        owner=user,
        place="Дом",
        time="10:00",
        action="Ванна с пеной",
        is_pleasant=True,
        duration=60,
        periodicity=1,
        is_public=False,
    )

    payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Прогулка",
        "is_pleasant": False,
        "reward": "Десерт",
        "related_habit": pleasant.id,
        "duration": 60,
        "periodicity": 1,
        "is_public": False,
    }

    resp = api_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_create_habit_related_habit_must_be_pleasant(api_client, user):
    not_pleasant = Habit.objects.create(
        owner=user,
        place="Дом",
        time="10:00",
        action="Не приятная",
        is_pleasant=False,
        reward="ok",
        duration=60,
        periodicity=1,
        is_public=False,
    )

    payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Прогулка",
        "is_pleasant": False,
        "related_habit": not_pleasant.id,
        "duration": 60,
        "periodicity": 1,
        "is_public": False,
    }

    resp = api_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_pleasant_habit_cannot_have_reward_or_related(api_client, user):
    payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Ванна",
        "is_pleasant": True,
        "reward": "Нельзя",
        "duration": 60,
        "periodicity": 1,
        "is_public": False,
    }

    resp = api_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_owner_can_delete_own_habit(api_client, user):
    habit = Habit.objects.create(
        owner=user,
        place="Дом",
        time="10:00",
        action="Удаляемая",
        is_pleasant=False,
        reward="Чай",
        duration=60,
        periodicity=1,
        is_public=False,
    )

    resp = api_client.delete(f"/api/habits/{habit.id}/")
    assert resp.status_code in (204, 200)
    assert Habit.objects.filter(id=habit.id).exists() is False


@pytest.mark.django_db
def test_user_cannot_delete_other_users_habit(api_client, user, other_user):
    habit = Habit.objects.create(
        owner=other_user,
        place="Дом",
        time="10:00",
        action="Чужая",
        is_pleasant=False,
        reward="Чай",
        duration=60,
        periodicity=1,
        is_public=False,
    )

    resp = api_client.delete(f"/api/habits/{habit.id}/")
    # Обычно либо 404 (скрываем существование), либо 403 (запрещено)
    assert resp.status_code in (403, 404)
    assert Habit.objects.filter(id=habit.id).exists() is True


@pytest.mark.django_db
def test_public_habits_list_is_read_only(api_client, user, other_user):
    Habit.objects.create(
        owner=other_user,
        place="Парк",
        time="10:00",
        action="Публичная",
        is_pleasant=False,
        reward="Кофе",
        duration=60,
        periodicity=1,
        is_public=True,
    )

    resp = api_client.get("/api/habits/public/")
    assert resp.status_code == 200

    data = resp.json()
    results = data.get("results", data)
    assert len(results) >= 1

    # Попытка POST в public endpoint должна быть запрещена
    create_resp = api_client.post("/api/habits/public/", {"action": "x"}, format="json")
    assert create_resp.status_code in (401, 403, 405)
