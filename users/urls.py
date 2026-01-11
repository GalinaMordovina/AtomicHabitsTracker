from django.urls import path

from .views import RegisterAPIView, SetTelegramChatIdAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("telegram/", SetTelegramChatIdAPIView.as_view(), name="set-telegram-chat-id"),
]
