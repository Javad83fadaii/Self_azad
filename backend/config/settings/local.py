"""Local development settings for the UFRS backend."""

import os

os.environ.setdefault("DEBUG", "1")
os.environ.setdefault("SECRET_KEY", "local-development-secret-key-for-self-food-project-2026-long")

from .base import *  # noqa: F403,F401
