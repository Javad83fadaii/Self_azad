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
        for module_name in ("config.settings.base", "config.settings.local"):
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


if __name__ == "__main__":
    unittest.main()
