from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication

from desktop.screens.main_window import MainWindow


def main() -> int:
    """Run the desktop application."""
    app = QApplication(sys.argv)
    app.setApplicationName("UFRS Student Desktop")
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    window = MainWindow()
    window.show()

    auto_exit_ms = os.getenv("UFRS_AUTO_EXIT_MS")
    if auto_exit_ms:
        QTimer.singleShot(int(auto_exit_ms), app.quit)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
