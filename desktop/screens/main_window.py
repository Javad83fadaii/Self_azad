from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Main desktop shell for the first phase of the project."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("UFRS - University Food Reservation System")
        self.setMinimumSize(720, 420)
        self._setup_ui()

    def _setup_ui(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("سامانه رزرو غذای سلف دانشگاه")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 28px; font-weight: 700; color: #1f2937; margin-bottom: 12px;"
        )

        student_button = QPushButton("ورود دانشجو")
        student_button.setMinimumHeight(48)

        admin_button = QPushButton("ورود مدیر")
        admin_button.setMinimumHeight(48)

        shared_style = """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """
        student_button.setStyleSheet(shared_style)
        admin_button.setStyleSheet(shared_style)

        layout.addWidget(title)
        layout.addWidget(student_button)
        layout.addWidget(admin_button)

        self.setCentralWidget(container)
