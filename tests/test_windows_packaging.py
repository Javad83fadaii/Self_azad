from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class WindowsPackagingTests(unittest.TestCase):
    def test_build_script_copies_runtime_configuration_templates(self) -> None:
        build_script = (PROJECT_ROOT / "build_windows.bat").read_text(encoding="utf-8")
        self.assertIn("desktop.env.example", build_script)
        self.assertIn("backend.production.env.example", build_script)
        self.assertIn("PyInstaller --noconfirm --clean", build_script)

    def test_installer_seeds_appdata_with_desktop_env_template(self) -> None:
        installer_script = (PROJECT_ROOT / "installer" / "ufrs_student_desktop.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn(r'{userappdata}\ufrs_student_desktop', installer_script)
        self.assertIn("desktop.env.example", installer_script)

    def test_required_packaging_templates_exist(self) -> None:
        for relative_path in (
            Path("desktop.env.example"),
            Path(".env.production.example"),
            Path("ufrs_student_desktop.spec"),
        ):
            self.assertTrue((PROJECT_ROOT / relative_path).is_file(), str(relative_path))


if __name__ == "__main__":
    unittest.main()
