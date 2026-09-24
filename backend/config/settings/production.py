"""Production settings for the UFRS backend."""

from __future__ import annotations

from .base import *  # noqa: F403,F401

DEBUG = False
SECRET_KEY = get_env("SECRET_KEY")  # noqa: F405
ALLOWED_HOSTS = [
    host.strip()
    for host in get_env("ALLOWED_HOSTS").split(",")  # noqa: F405
    if host.strip()
]

DATABASES = {
    "default": build_mysql_database_config(require_values=True)  # noqa: F405
}

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = get_bool_env("SECURE_SSL_REDIRECT", True)  # noqa: F405
SECURE_HSTS_SECONDS = get_int_env("SECURE_HSTS_SECONDS", 31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_bool_env("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)  # noqa: F405
SECURE_HSTS_PRELOAD = get_bool_env("SECURE_HSTS_PRELOAD", True)  # noqa: F405
