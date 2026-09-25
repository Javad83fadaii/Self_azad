from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from desktop.runtime import app_data_dir, icon_path, iter_env_candidates, load_runtime_environment


class DesktopRuntimeTests(unittest.TestCase):
    def test_load_runtime_environment_uses_explicit_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "desktop.env"
            env_file.write_text("UFRS_RUNTIME_TEST_FLAG=loaded\n", encoding="utf-8")

            with patch.dict(os.environ, {"UFRS_ENV_FILE": str(env_file)}, clear=False):
                os.environ.pop("UFRS_RUNTIME_TEST_FLAG", None)
                loaded_file = load_runtime_environment()
                self.assertEqual(loaded_file, env_file)
                self.assertEqual(os.getenv("UFRS_RUNTIME_TEST_FLAG"), "loaded")

        os.environ.pop("UFRS_RUNTIME_TEST_FLAG", None)

    def test_app_data_dir_prefers_appdata_environment(self) -> None:
        with patch.dict(os.environ, {"APPDATA": r"C:\Temp\AppData"}, clear=False):
            self.assertEqual(app_data_dir(), Path(r"C:\Temp\AppData") / "ufrs_student_desktop")

    def test_icon_path_points_to_packaged_resource(self) -> None:
        self.assertEqual(icon_path().name, "app_icon.ico")

    def test_runtime_checks_desktop_env_next_to_executable(self) -> None:
        executable_root = Path(r"C:\Apps\UFRS")
        with patch("desktop.runtime.executable_dir", return_value=executable_root):
            candidates = iter_env_candidates()
        self.assertIn(executable_root / "desktop.env", candidates)
        self.assertIn(executable_root / "config" / "desktop.env", candidates)


if __name__ == "__main__":
    unittest.main()
