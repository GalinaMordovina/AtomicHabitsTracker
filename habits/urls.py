from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import HabitViewSet, PublicHabitViewSet

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habits")

public_list = PublicHabitViewSet.as_view({"get": "list"})

urlpatterns = [
    # Публичные привычки
    path("habits/public/", public_list, name="public-habits"),
    path("", include(router.urls)),

]
