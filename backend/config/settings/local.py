"""Local development settings for the UFRS backend."""

import os

os.environ.setdefault("DEBUG", "1")
os.environ.setdefault("SECRET_KEY", "local-development-secret-key-for-self-food-project-2026-long")
os.environ.setdefault("DB_NAME", "ufrs_db")
os.environ.setdefault("DB_USER", "root")
os.environ.setdefault("DB_PASSWORD", "")
os.environ.setdefault("DB_HOST", "127.0.0.1")
os.environ.setdefault("DB_PORT", "3306")

from .base import *  # noqa: F403,F401

DATABASES = {
    "default": build_mysql_database_config()  # noqa: F405
}
