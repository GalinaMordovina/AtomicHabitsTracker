from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # jwt
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/users/', include('users.urls')),
    path("api/", include("habits.urls")),

    # OpenAPI schema (машиночитаемое описание API)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI (интерактивная документация)
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Redoc (красивое “чтение” документации)
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
