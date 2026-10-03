from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class BackendSettingsTests(unittest.TestCase):
    def tearDown(self) -> None:
        for module_name in (
            "config.settings.base",
            "config.settings.local",
            "config.settings.production",
        ):
            sys.modules.pop(module_name, None)

    def test_local_settings_fall_back_to_sqlite_without_database_env(self) -> None:
        env_overrides = {
            "DJANGO_SETTINGS_MODULE": "config.settings.local",
            "DEBUG": "1",
            "SECRET_KEY": "local-test-secret",
            "DB_ENGINE": "sqlite",
        }
        removed_keys = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "LOCAL_DB_ENGINE"]

        with patch.dict(os.environ, env_overrides, clear=False):
            for key in removed_keys:
                os.environ.pop(key, None)
            local_settings = importlib.import_module("config.settings.local")

        self.assertEqual(local_settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3")

    def test_production_settings_require_allowed_hosts(self) -> None:
        env_overrides = {
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
            "DEBUG": "False",
            "SECRET_KEY": "production-secret-key-for-phase7-tests-with-sufficient-entropy-12345",
            "ALLOWED_HOSTS": "",
            "DB_NAME": "ufrs",
            "DB_USER": "ufrs",
            "DB_PASSWORD": "strong-password",
            "DB_HOST": "127.0.0.1",
            "DB_PORT": "3306",
        }

        with patch.dict(os.environ, env_overrides, clear=False):
            with self.assertRaises(RuntimeError):
                importlib.import_module("config.settings.production")

    def test_production_settings_enable_secure_defaults_and_logging(self) -> None:
        env_overrides = {
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
            "DEBUG": "False",
            "SECRET_KEY": "production-secret-key-for-phase7-tests-with-sufficient-entropy-67890",
            "ALLOWED_HOSTS": "example.com,www.example.com",
            "DB_NAME": "ufrs",
            "DB_USER": "ufrs",
            "DB_PASSWORD": "strong-password",
            "DB_HOST": "127.0.0.1",
            "DB_PORT": "3306",
        }

        with patch.dict(os.environ, env_overrides, clear=False):
            production_settings = importlib.import_module("config.settings.production")

        self.assertFalse(production_settings.DEBUG)
        self.assertTrue(production_settings.SESSION_COOKIE_SECURE)
        self.assertTrue(production_settings.CSRF_COOKIE_SECURE)
        self.assertEqual(
            production_settings.DATABASES["default"]["ENGINE"],
            "django.db.backends.mysql",
        )
        self.assertIn("django.security", production_settings.LOGGING["loggers"])
        self.assertIn("students", production_settings.LOGGING["loggers"])


if __name__ == "__main__":
    unittest.main()
