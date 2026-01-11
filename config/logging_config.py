from __future__ import annotations

from pathlib import Path


# Он тут, потому-что конфиг логирования здесь удобно менять/расширять
def build_logging_config(base_dir: Path) -> dict:
    """
    Возвращает словарь LOGGING для Django.
    """
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "[{levelname}] {asctime} {name}: {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "celery_file": {
                "class": "logging.FileHandler",
                "filename": str(log_dir / "celery.log"),
                "formatter": "simple",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            # наши задачи / интеграции
            "notifications": {
                "handlers": ["console", "celery_file"],
                "level": "INFO",
                "propagate": False,
            },
            # django можно оставить только в консоль
            "django": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }
