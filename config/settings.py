from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta
from config.logging_config import build_logging_config

# Загружаем переменные окружения из файла .env
load_dotenv()  # чтобы перезаписывать можно добавить (override=True)

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent
# Логирование
LOGGING = build_logging_config(BASE_DIR)

SECRET_KEY = os.getenv('SECRET_KEY')

# Режим отладки: Включаем DEBUG только если в .env указано DEBUG=True
DEBUG = True if os.getenv('DEBUG') == "True" else False

# Список разрешённых хостов
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

# CORS
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True") == "True"

# без списка origins запросы с фронта не пройдут
#CORS_ALLOWED_ORIGINS = (
#    [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
#    if not CORS_ALLOW_ALL_ORIGINS
#    else []
#)

# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # сторонние
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_beat',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'corsheaders',

    # наши приложения
    'users',
    'habits',
    'notifications',

]

# Middleware (промежуточные слои)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Основной файл маршрутизации
ROOT_URLCONF = 'config.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Точка входа WSGI
WSGI_APPLICATION = 'config.wsgi.application'


## База данных
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "habits"),
            "USER": os.getenv("POSTGRES_USER", "habits"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "habits"),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Валидация паролей
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Локализация
LANGUAGE_CODE = 'ru'         # язык интерфейса

TIME_ZONE = 'Europe/Moscow'  # часовой пояс

USE_I18N = True

USE_TZ = True

USE_L10N = True

# Тип поля для первичных ключей (убирает предупреждения W042)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Статические и медиа-файлы
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# DRF: базовые настройки API
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Документация drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Atomic Habits Tracker API",
    "DESCRIPTION": "API для трекера полезных привычек.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# SimpleJWT: настройки времени жизни токенов
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # короткий (для запросов)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # длинный (для обновления Access)
}

# Настройки для Celery
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

# URL-адрес брокера сообщений
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# URL-адрес брокера результатов, также Redis
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Часовой пояс для работы Celery
CELERY_TIMEZONE = TIME_ZONE

# Флаг отслеживания выполнения задач
CELERY_TASK_TRACK_STARTED = True

# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
