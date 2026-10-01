"""Base Django settings for the UFRS backend."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BACKEND_DIR.parent


def iter_backend_env_candidates() -> list[Path]:
    """Return backend environment files in load priority order."""
    explicit_env = os.getenv("BACKEND_ENV_FILE")
    candidates: list[Path] = []

    if explicit_env:
        candidates.append(Path(explicit_env).expanduser())

    candidates.extend(
        [
            ROOT_DIR / ".env",
            ROOT_DIR / ".env.local",
            ROOT_DIR / ".env.production",
            BACKEND_DIR / ".env",
        ]
    )

    # Preserve order while removing duplicates.
    unique_candidates: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique_candidates.append(candidate)
            seen.add(candidate)
    return unique_candidates


def load_backend_environment() -> Path | None:
    """Load the first available backend environment file."""
    for env_file in iter_backend_env_candidates():
        if env_file.is_file():
            load_dotenv(env_file, override=False)
            return env_file
    return None


BACKEND_ENV_FILE = load_backend_environment()


def get_env(name: str, default: str | None = None) -> str:
    """Read an environment variable with an optional fallback."""
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_bool_env(name: str, default: bool = False) -> bool:
    """Parse common truthy values from environment variables."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_int_env(name: str, default: int) -> int:
    """Parse integer environment variables with a fallback value."""
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def get_list_env(name: str, default: str = "") -> list[str]:
    """Parse comma-separated environment variables into a normalized list."""
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def get_optional_path_env(name: str) -> Path | None:
    """Return a normalized optional filesystem path from the environment."""
    value = os.getenv(name, "").strip()
    if not value:
        return None
    return Path(value).expanduser()


def build_mysql_database_config(
    *,
    require_values: bool = False,
    defaults: dict[str, str] | None = None,
) -> dict[str, object]:
    """Build the MySQL database configuration from environment variables."""
    defaults = defaults or {}
    reader = get_env if require_values else os.getenv

    name = reader("DB_NAME", defaults.get("DB_NAME"))
    user = reader("DB_USER", defaults.get("DB_USER"))
    password = reader("DB_PASSWORD", defaults.get("DB_PASSWORD"))
    host = reader("DB_HOST", defaults.get("DB_HOST"))
    port = reader("DB_PORT", defaults.get("DB_PORT"))

    if None in {name, user, password, host, port}:
        missing = [
            key
            for key, value in {
                "DB_NAME": name,
                "DB_USER": user,
                "DB_PASSWORD": password,
                "DB_HOST": host,
                "DB_PORT": port,
            }.items()
            if value is None
        ]
        raise RuntimeError(
            "Missing required database environment variables: " + ", ".join(missing)
        )

    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": name,
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }


def build_sqlite_database_config(name: str | Path | None = None) -> dict[str, object]:
    """Build a SQLite configuration for local development and validation."""
    database_name = Path(name) if name is not None else ROOT_DIR / "dev_db.sqlite3"
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": database_name,
    }


DEBUG = get_bool_env("DEBUG", False)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "local-development-secret-key-for-self-food-project-2026-long"
    else:
        raise RuntimeError("Missing required environment variable: SECRET_KEY")
ALLOWED_HOSTS = get_list_env("ALLOWED_HOSTS", "127.0.0.1,localhost")
WEB_FRONTEND_URL = os.getenv("WEB_FRONTEND_URL", "").strip()
WEB_ALLOWED_ORIGINS = get_list_env("WEB_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = get_list_env("CSRF_TRUSTED_ORIGINS")
if WEB_FRONTEND_URL and WEB_FRONTEND_URL not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(WEB_FRONTEND_URL)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "accounts.apps.AccountsConfig",
    "students.apps.StudentsConfig",
    "meals.apps.MealsConfig",
    "reservations.apps.ReservationsConfig",
    "reports.apps.ReportsConfig",
    "dashboard.apps.DashboardConfig",
    "audit_logs.apps.AuditLogsConfig",
    "common.apps.CommonConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BACKEND_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BACKEND_DIR / "staticfiles"
STATICFILES_DIRS = [BACKEND_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BACKEND_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "auth": "10/min",
    },
}

SESSION_COOKIE_HTTPONLY = get_bool_env("SESSION_COOKIE_HTTPONLY", True)
CSRF_COOKIE_HTTPONLY = get_bool_env("CSRF_COOKIE_HTTPONLY", False)
SESSION_COOKIE_SECURE = get_bool_env("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = get_bool_env("CSRF_COOKIE_SECURE", not DEBUG)
SESSION_COOKIE_SAMESITE = get_env("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = get_env("CSRF_COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_AGE = get_int_env("SESSION_COOKIE_AGE", 1209600)
SESSION_EXPIRE_AT_BROWSER_CLOSE = get_bool_env("SESSION_EXPIRE_AT_BROWSER_CLOSE", False)
SECURE_SSL_REDIRECT = get_bool_env("SECURE_SSL_REDIRECT", not DEBUG)
SECURE_HSTS_SECONDS = get_int_env("SECURE_HSTS_SECONDS", 31536000 if not DEBUG else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_bool_env("SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = get_bool_env("SECURE_HSTS_PRELOAD", not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
CSRF_FAILURE_VIEW = "common.error_handlers.csrf_failure"

if get_bool_env("USE_X_FORWARDED_PROTO", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = get_bool_env("USE_X_FORWARDED_HOST", True)

LOG_LEVEL = get_env("LOG_LEVEL", "INFO").upper()
DJANGO_LOG_LEVEL = get_env("DJANGO_LOG_LEVEL", "WARNING").upper()
ENABLE_FILE_LOGGING = get_bool_env("ENABLE_FILE_LOGGING", False)
LOG_DIR = get_optional_path_env("LOG_DIR")
if ENABLE_FILE_LOGGING:
    LOG_DIR = LOG_DIR or (ROOT_DIR / "logs")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOG_LEVEL,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "meals": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "reservations": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "reports": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "audit_logs": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

if ENABLE_FILE_LOGGING and LOG_DIR is not None:
    LOGGING["handlers"]["application_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "standard",
        "filename": str(LOG_DIR / "application.log"),
        "maxBytes": get_int_env("APP_LOG_MAX_BYTES", 10 * 1024 * 1024),
        "backupCount": get_int_env("APP_LOG_BACKUP_COUNT", 5),
        "level": LOG_LEVEL,
        "encoding": "utf-8",
    }
    LOGGING["handlers"]["error_file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "standard",
        "filename": str(LOG_DIR / "error.log"),
        "maxBytes": get_int_env("ERROR_LOG_MAX_BYTES", 10 * 1024 * 1024),
        "backupCount": get_int_env("ERROR_LOG_BACKUP_COUNT", 10),
        "level": "WARNING",
        "encoding": "utf-8",
    }
    for logger_name in ("django", "django.request", "accounts", "meals", "reservations", "reports", "audit_logs"):
        LOGGING["loggers"][logger_name]["handlers"].append("application_file")
    for logger_name in ("django", "django.request", "django.db.backends"):
        LOGGING["loggers"][logger_name]["handlers"].append("error_file")
