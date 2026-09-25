"""Local development settings for the UFRS backend."""

import os

os.environ.setdefault("DEBUG", "1")
os.environ.setdefault("SECRET_KEY", "local-development-secret-key-for-self-food-project-2026-long")

from .base import *  # noqa: F403,F401

local_database_engine = (os.getenv("LOCAL_DB_ENGINE") or os.getenv("DB_ENGINE") or "sqlite").strip().lower()

if local_database_engine == "mysql" or os.getenv("DB_NAME"):
    DATABASES = {
        "default": build_mysql_database_config(require_values=True)  # noqa: F405
    }
else:
    DATABASES = {
        "default": build_sqlite_database_config()  # noqa: F405
    }
