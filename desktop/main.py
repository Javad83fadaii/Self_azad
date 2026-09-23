from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

try:
    from .screens.main_window import MainWindow
except ImportError:
    from screens.main_window import MainWindow


def main() -> int:
    """Run the desktop application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
