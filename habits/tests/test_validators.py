import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from habits.models import Habit


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="val_user", password="pass12345")


@pytest.fixture
def other_user():
    return User.objects.create_user(username="val_user2", password="pass12345")


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
def test_cannot_set_reward_and_related_habit_together(auth_client, other_user):
    pleasant = Habit.objects.create(
        owner=other_user,
        place="Дом",
        time="10:00",
        action="Ванна с пеной",
        is_pleasant=True,
        duration=60,
        periodicity=1,
        is_public=False,
    )

    payload = {
        "place": "Парк",
        "time": "10:00",
        "action": "Погулять",
        "is_pleasant": False,
        "duration": 60,
        "periodicity": 1,
        "reward": "Кофе",
        "related_habit": pleasant.id,
        "is_public": False,
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "Нельзя одновременно" in str(resp.data)


@pytest.mark.django_db
def test_duration_cannot_be_more_than_120(auth_client):
    payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Отжимания",
        "is_pleasant": False,
        "duration": 121,
        "periodicity": 1,
        "is_public": False,
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "120" in str(resp.data)


@pytest.mark.django_db
def test_periodicity_cannot_be_more_than_7(auth_client):
    payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Читать книгу",
        "is_pleasant": False,
        "duration": 60,
        "periodicity": 8,
        "is_public": False,
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "7" in str(resp.data)


@pytest.mark.django_db
def test_related_habit_must_be_pleasant(auth_client, other_user):
    not_pleasant = Habit.objects.create(
        owner=other_user,
        place="Дом",
        time="10:00",
        action="Полезная (не приятная)",
        is_pleasant=False,
        duration=60,
        periodicity=1,
        is_public=False,
    )

    payload = {
        "place": "Парк",
        "time": "10:00",
        "action": "Прогулка",
        "is_pleasant": False,
        "duration": 60,
        "periodicity": 1,
        "related_habit": not_pleasant.id,
        "is_public": False,
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "должна быть приятной" in str(resp.data)


@pytest.mark.django_db
def test_pleasant_habit_cannot_have_reward_or_related_habit(auth_client, other_user):
    pleasant_reward_payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Посмотреть сериал",
        "is_pleasant": True,
        "duration": 60,
        "periodicity": 1,
        "reward": "Кофе",
        "is_public": False,
    }

    resp = auth_client.post("/api/habits/", pleasant_reward_payload, format="json")
    assert resp.status_code == 400
    assert "приятной привычки" in str(resp.data)

    pleasant = Habit.objects.create(
        owner=other_user,
        place="Дом",
        time="10:00",
        action="Ванна",
        is_pleasant=True,
        duration=60,
        periodicity=1,
        is_public=False,
    )

    pleasant_related_payload = {
        "place": "Дом",
        "time": "10:00",
        "action": "Ещё одна приятная",
        "is_pleasant": True,
        "duration": 60,
        "periodicity": 1,
        "related_habit": pleasant.id,
        "is_public": False,
    }

    resp2 = auth_client.post("/api/habits/", pleasant_related_payload, format="json")
    assert resp2.status_code == 400
    assert "приятной привычки" in str(resp2.data)


@pytest.mark.django_db
def test_patch_keeps_instance_values_and_still_validates(auth_client, other_user):
    pleasant = Habit.objects.create(
        owner=other_user,
        place="Дом",
        time="10:00",
        action="Ванна",
        is_pleasant=True,
        duration=60,
        periodicity=1,
        is_public=False,
    )

    # Создаём полезную привычку с reward
    create_payload = {
        "place": "Парк",
        "time": "10:00",
        "action": "Прогулка",
        "is_pleasant": False,
        "duration": 60,
        "periodicity": 1,
        "reward": "Кофе",
        "is_public": False,
    }
    created = auth_client.post("/api/habits/", create_payload, format="json")
    habit_id = created.data["id"]

    # PATCH: добавляем related_habit, reward НЕ передаём.
    # Но reward уже есть в instance -> валидатор должен запретить.
    patch_payload = {"related_habit": pleasant.id}
    resp = auth_client.patch(f"/api/habits/{habit_id}/", patch_payload, format="json")

    assert resp.status_code == 400
    assert "Нельзя одновременно" in str(resp.data)
