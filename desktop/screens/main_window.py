from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from desktop.api.client import ApiClient, ApiError
from desktop.auth.session import AuthSession
from desktop.runtime import icon_path
from desktop.services.student_service import StudentApiService
from desktop.utils.errors import translate_error
from desktop.utils.formatters import (
    build_last_reservation_text,
    build_schedule_status,
    format_schedule_day_heading,
    format_date,
    format_datetime,
    format_reservation_status,
    is_future_active_reservation,
    is_schedule_reservable,
)


class LoginPage(QWidget):
    login_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(40, 40, 40, 40)
        root_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setMaximumWidth(440)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(18)

        title = QLabel("ورود دانشجو")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("برای مشاهده برنامه غذایی و رزروها وارد حساب خود شوید.")
        subtitle.setObjectName("mutedLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(12)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("کد دانشجویی")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._emit_login_requested)

        form_layout.addRow("کد دانشجویی:", self.username_input)
        form_layout.addRow("رمز عبور:", self.password_input)

        self.feedback_label = QLabel("")
        self.feedback_label.setObjectName("errorLabel")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.hide()

        self.login_button = QPushButton("ورود")
        self.login_button.setMinimumHeight(44)
        self.login_button.clicked.connect(self._emit_login_requested)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addLayout(form_layout)
        card_layout.addWidget(self.feedback_label)
        card_layout.addWidget(self.login_button)

        root_layout.addWidget(card)

    def _emit_login_requested(self) -> None:
        self.feedback_label.hide()
        self.login_requested.emit(
            self.username_input.text().strip(),
            self.password_input.text(),
        )

    def set_busy(self, busy: bool) -> None:
        self.login_button.setDisabled(busy)
        self.username_input.setDisabled(busy)
        self.password_input.setDisabled(busy)
        self.login_button.setText("در حال ورود..." if busy else "ورود")

    def show_error(self, message: str) -> None:
        self.feedback_label.setText(message)
        self.feedback_label.show()

    def clear_form(self) -> None:
        self.password_input.clear()
        self.feedback_label.hide()


class SectionHeader(QWidget):
    def __init__(self, title: str, description: str, action_button: QPushButton) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        text_wrapper = QVBoxLayout()
        text_wrapper.setContentsMargins(0, 0, 0, 0)
        text_wrapper.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        description_label = QLabel(description)
        description_label.setObjectName("mutedLabel")
        description_label.setWordWrap(True)

        text_wrapper.addWidget(title_label)
        text_wrapper.addWidget(description_label)

        layout.addLayout(text_wrapper, 1)
        layout.addWidget(action_button, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "-") -> None:
        super().__init__()
        self.setObjectName("statCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        self.value_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class DashboardPage(QWidget):
    refresh_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        refresh_button = QPushButton("به‌روزرسانی")
        refresh_button.clicked.connect(self.refresh_requested.emit)

        layout.addWidget(
            SectionHeader(
                "داشبورد",
                "خلاصه‌ای از اطلاعات دانشجو و آخرین وضعیت رزروها در این بخش نمایش داده می‌شود.",
                refresh_button,
            )
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        self.student_name_card = StatCard("نام دانشجو")
        self.student_code_card = StatCard("کد دانشجویی")
        self.future_count_card = StatCard("تعداد رزروهای آینده")
        self.last_reservation_card = StatCard("آخرین رزرو")

        grid.addWidget(self.student_name_card, 0, 0)
        grid.addWidget(self.student_code_card, 0, 1)
        grid.addWidget(self.future_count_card, 1, 0)
        grid.addWidget(self.last_reservation_card, 1, 1)

        layout.addLayout(grid)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def set_dashboard_data(self, profile: dict[str, Any], reservations: list[dict[str, Any]]) -> None:
        future_reservations = [
            reservation
            for reservation in reservations
            if is_future_active_reservation(reservation)
        ]
        latest_reservation = reservations[0] if reservations else None

        self.student_name_card.set_value(profile.get("full_name") or "-")
        self.student_code_card.set_value(profile.get("student_code") or "-")
        self.future_count_card.set_value(str(len(future_reservations)))
        self.last_reservation_card.set_value(build_last_reservation_text(latest_reservation))


class MealSchedulePage(QWidget):
    refresh_requested = Signal()
    reserve_requested = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        refresh_button = QPushButton("به‌روزرسانی")
        refresh_button.clicked.connect(self.refresh_requested.emit)

        layout.addWidget(
            SectionHeader(
                "برنامه غذایی",
                "غذاهای روزهای آینده را ببینید و مستقیما از طریق REST API رزرو خود را ثبت کنید.",
                refresh_button,
            )
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)
        self.content_layout.addItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area, 1)

    def set_schedules(
        self,
        schedules: list[dict[str, Any]],
        image_loader: Callable[[str | None], QPixmap | None],
    ) -> None:
        self._clear_layout(self.content_layout)

        if not schedules:
            empty_label = QLabel("هنوز برنامه غذایی فعالی برای روزهای آینده ثبت نشده است.")
            empty_label.setObjectName("emptyStateLabel")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(empty_label)
            self.content_layout.addStretch(1)
            return

        grouped_schedules: dict[str, list[dict[str, Any]]] = {}
        for schedule in schedules:
            grouped_schedules.setdefault(schedule.get("date") or "-", []).append(schedule)

        for schedule_date, date_schedules in grouped_schedules.items():
            day_header = QLabel(format_schedule_day_heading(schedule_date))
            day_header.setObjectName("sectionDayHeader")
            self.content_layout.addWidget(day_header)

            for schedule in date_schedules:
                self.content_layout.addWidget(self._build_schedule_card(schedule, image_loader))

        self.content_layout.addStretch(1)

    def _build_schedule_card(
        self,
        schedule: dict[str, Any],
        image_loader: Callable[[str | None], QPixmap | None],
    ) -> QWidget:
        meal = schedule.get("meal") or {}
        status_text = build_schedule_status(schedule)
        can_reserve = is_schedule_reservable(schedule)

        card = QFrame()
        card.setObjectName("contentCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        image_label = QLabel("تصویر غذا")
        image_label.setObjectName("imagePreview")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setMinimumSize(160, 120)
        image_label.setMaximumSize(160, 120)

        pixmap = image_loader(meal.get("image"))
        if pixmap:
            image_label.setPixmap(
                pixmap.scaled(
                    160,
                    120,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            image_label.setText("بدون تصویر")

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        title = QLabel(meal.get("name", "-"))
        title.setObjectName("cardTitle")

        date_label = QLabel(f"تاریخ سرو: {format_date(schedule.get('date'))}")
        date_label.setObjectName("mutedLabel")

        stats_card = QFrame()
        stats_card.setObjectName("metaStrip")
        stats_layout = QGridLayout(stats_card)
        stats_layout.setContentsMargins(12, 12, 12, 12)
        stats_layout.setHorizontalSpacing(12)
        stats_layout.setVerticalSpacing(8)

        for index, (label_text, value_text) in enumerate(
            [
                ("ظرفیت", str(schedule.get("capacity", "-"))),
                ("تعداد رزرو", str(schedule.get("reserved_count", "-"))),
                ("ظرفیت باقی مانده", str(schedule.get("remaining_capacity", "-"))),
                ("وضعیت", status_text),
            ]
        ):
            label_widget = QLabel(label_text)
            label_widget.setObjectName("metaLabel")
            value_widget = QLabel(value_text)
            value_widget.setObjectName("metaValue")
            stats_layout.addWidget(label_widget, 0, index)
            stats_layout.addWidget(value_widget, 1, index)

        window_label = QLabel(
            f"بازه رزرو: {format_datetime(schedule.get('reservation_open_at'))}"
            f" تا {format_datetime(schedule.get('reservation_close_at'))}"
        )
        window_label.setObjectName("mutedLabel")
        window_label.setWordWrap(True)

        action_button = QPushButton("رزرو")
        action_button.setEnabled(can_reserve)
        action_button.clicked.connect(lambda _=False, item=schedule: self.reserve_requested.emit(item))

        info_layout.addWidget(title)
        info_layout.addWidget(date_label)
        info_layout.addWidget(stats_card)
        info_layout.addWidget(window_label)
        info_layout.addWidget(action_button, 0, Qt.AlignmentFlag.AlignRight)
        info_layout.addStretch(1)

        layout.addWidget(image_label, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(info_layout, 1)
        return card

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                MealSchedulePage._clear_layout(child_layout)  # type: ignore[arg-type]


class MyReservationsPage(QWidget):
    refresh_requested = Signal()
    cancel_requested = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        refresh_button = QPushButton("به‌روزرسانی")
        refresh_button.clicked.connect(self.refresh_requested.emit)

        layout.addWidget(
            SectionHeader(
                "رزروهای من",
                "فهرست رزروهای ثبت‌شده، وضعیت هر رزرو و امکان لغو رزروهای فعال را از این بخش مدیریت کنید.",
                refresh_button,
            )
        )

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["کد رزرو", "تاریخ", "غذا", "وضعیت", "عملیات"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addWidget(self.table, 1)

    def set_reservations(self, reservations: list[dict[str, Any]]) -> None:
        for row_index in range(self.table.rowCount()):
            widget = self.table.cellWidget(row_index, 4)
            if widget is not None:
                widget.deleteLater()

        self.table.clearContents()
        self.table.setRowCount(len(reservations))

        for row_index, reservation in enumerate(reservations):
            self._set_item(row_index, 0, reservation.get("reservation_code", "-"))
            self._set_item(
                row_index,
                1,
                format_date(reservation.get("schedule_date") or reservation.get("reservation_date")),
            )
            self._set_item(row_index, 2, reservation.get("meal_name", "-"))
            self._set_item(row_index, 3, format_reservation_status(reservation.get("status")))

            if reservation.get("status") == "RESERVED":
                action_button = QPushButton("لغو")
                action_button.clicked.connect(
                    lambda _=False, item=reservation: self.cancel_requested.emit(item)
                )
                self.table.setCellWidget(row_index, 4, action_button)
            else:
                self._set_item(row_index, 4, "-")

        self.table.resizeColumnsToContents()

    def _set_item(self, row: int, column: int, value: str) -> None:
        item = QTableWidgetItem(value)
        item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
        self.table.setItem(row, column, item)


class ProfilePage(QWidget):
    refresh_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.value_labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        refresh_button = QPushButton("به‌روزرسانی")
        refresh_button.clicked.connect(self.refresh_requested.emit)

        layout.addWidget(
            SectionHeader(
                "پروفایل",
                "اطلاعات حساب دانشجویی شما در این صفحه نمایش داده می‌شود.",
                refresh_button,
            )
        )

        card = QFrame()
        card.setObjectName("contentCard")

        form_layout = QFormLayout(card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(14)

        for key, label in [
            ("full_name", "نام و نام خانوادگی:"),
            ("student_code", "کد دانشجویی:"),
            ("phone_number", "شماره تماس:"),
            ("username", "نام کاربری:"),
            ("role", "نقش:"),
            ("is_active", "وضعیت حساب:"),
        ]:
            value_label = QLabel("-")
            value_label.setObjectName("profileValue")
            value_label.setWordWrap(True)
            self.value_labels[key] = value_label
            form_layout.addRow(label, value_label)

        layout.addWidget(card)
        layout.addStretch(1)

    def set_profile(self, profile: dict[str, Any]) -> None:
        self.value_labels["full_name"].setText(profile.get("full_name") or "-")
        self.value_labels["student_code"].setText(profile.get("student_code") or "-")
        self.value_labels["phone_number"].setText(profile.get("phone_number") or "-")
        self.value_labels["username"].setText(profile.get("username") or "-")
        self.value_labels["role"].setText("دانشجو" if profile.get("role") == "STUDENT" else "-")
        self.value_labels["is_active"].setText("فعال" if profile.get("is_active") else "غیرفعال")


class MainWindow(QMainWindow):
    """Student desktop UI for phase 4 based entirely on REST APIs."""

    def __init__(self) -> None:
        super().__init__()
        self.api_client = ApiClient()
        self.session = AuthSession()
        self.student_service = StudentApiService(self.api_client)
        self.profile_data: dict[str, Any] = {}
        self.reservations_data: list[dict[str, Any]] = []
        self.schedules_data: list[dict[str, Any]] = []
        self.navigation_buttons: dict[str, QPushButton] = {}
        self._busy_state = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("سامانه رزرو غذای سلف دانشگاه - نسخه دانشجو")
        self.setMinimumSize(1200, 760)
        app_icon = icon_path()
        if app_icon.is_file():
            self.setWindowIcon(QIcon(str(app_icon)))
        self.setStatusBar(QStatusBar(self))

        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(24, 24, 24, 24)

        self.root_stack = QStackedWidget()
        self.login_page = LoginPage()
        self.login_page.login_requested.connect(self._handle_login)
        self.root_stack.addWidget(self.login_page)
        self.root_stack.addWidget(self._build_authenticated_shell())

        root_layout.addWidget(self.root_stack)
        self.setCentralWidget(root)
        self._apply_styles()

    def _build_authenticated_shell(self) -> QWidget:
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(18)

        header = QFrame()
        header.setObjectName("headerCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 18)

        title_wrapper = QVBoxLayout()
        title_wrapper.setContentsMargins(0, 0, 0, 0)
        title_wrapper.setSpacing(6)

        title = QLabel("نسخه دانشجویی سامانه رزرو غذا")
        title.setObjectName("headerTitle")

        self.header_subtitle = QLabel("برای شروع وارد حساب دانشجویی خود شوید.")
        self.header_subtitle.setObjectName("mutedLabel")
        self.header_subtitle.setWordWrap(True)

        title_wrapper.addWidget(title)
        title_wrapper.addWidget(self.header_subtitle)

        self.logout_button = QPushButton("خروج از حساب")
        self.logout_button.clicked.connect(self._logout)

        header_layout.addLayout(title_wrapper, 1)
        header_layout.addWidget(self.logout_button, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        shell_layout.addWidget(header)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(18)

        navigation_card = QFrame()
        navigation_card.setObjectName("sidebarCard")
        navigation_card.setMinimumWidth(220)
        navigation_layout = QVBoxLayout(navigation_card)
        navigation_layout.setContentsMargins(14, 14, 14, 14)
        navigation_layout.setSpacing(10)

        nav_title = QLabel("منوی دانشجو")
        nav_title.setObjectName("sidebarTitle")
        navigation_layout.addWidget(nav_title)

        for key, label in [
            ("dashboard", "داشبورد"),
            ("schedules", "برنامه غذایی"),
            ("reservations", "رزروهای من"),
            ("profile", "پروفایل"),
        ]:
            button = QPushButton(label)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, page_key=key: self._switch_page(page_key))
            self.navigation_buttons[key] = button
            navigation_layout.addWidget(button)

        navigation_layout.addStretch(1)

        content_card = QFrame()
        content_card.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(18, 18, 18, 18)

        self.page_stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.dashboard_page.refresh_requested.connect(self.refresh_all_data)
        self.schedules_page = MealSchedulePage()
        self.schedules_page.refresh_requested.connect(self.refresh_all_data)
        self.schedules_page.reserve_requested.connect(self._reserve_schedule)
        self.reservations_page = MyReservationsPage()
        self.reservations_page.refresh_requested.connect(self.refresh_all_data)
        self.reservations_page.cancel_requested.connect(self._cancel_reservation)
        self.profile_page = ProfilePage()
        self.profile_page.refresh_requested.connect(self.refresh_all_data)

        self.page_stack.addWidget(self.dashboard_page)
        self.page_stack.addWidget(self.schedules_page)
        self.page_stack.addWidget(self.reservations_page)
        self.page_stack.addWidget(self.profile_page)

        content_layout.addWidget(self.page_stack)

        body_layout.addWidget(navigation_card)
        body_layout.addWidget(content_card, 1)

        shell_layout.addLayout(body_layout, 1)
        return shell

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #f3f7fb;
                color: #14213d;
                font-size: 14px;
            }
            QFrame#loginCard, QFrame#headerCard, QFrame#sidebarCard, QFrame#contentContainer,
            QFrame#statCard, QFrame#contentCard {
                background: rgba(255, 255, 255, 0.94);
                border: 1px solid #d9e3f0;
                border-radius: 18px;
            }
            QLabel#pageTitle {
                font-size: 24px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#headerTitle {
                font-size: 22px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#sidebarTitle {
                font-size: 16px;
                font-weight: 700;
                color: #334155;
                padding: 4px 6px 10px 6px;
            }
            QLabel#statTitle {
                color: #64748b;
                font-size: 13px;
            }
            QLabel#statValue {
                font-size: 20px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#cardTitle {
                font-size: 18px;
                font-weight: 700;
                color: #0f172a;
            }
            QLabel#mutedLabel {
                color: #64748b;
            }
            QLabel#errorLabel {
                color: #b91c1c;
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel#emptyStateLabel {
                color: #64748b;
                font-size: 15px;
                padding: 24px;
            }
            QLabel#sectionDayHeader {
                color: #0f172a;
                font-size: 17px;
                font-weight: 700;
                padding: 6px 2px 2px 2px;
            }
            QLabel#profileValue {
                color: #0f172a;
                font-weight: 600;
            }
            QLabel#imagePreview {
                background: #e2e8f0;
                border: 1px solid #cbd5e1;
                border-radius: 14px;
                color: #475569;
            }
            QLabel#metaLabel {
                color: #64748b;
                font-size: 12px;
            }
            QLabel#metaValue {
                color: #0f172a;
                font-size: 14px;
                font-weight: 700;
            }
            QLineEdit, QTableWidget {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
                padding: 10px 12px;
            }
            QFrame#metaStrip {
                background: #f8fbff;
                border: 1px solid #dbe7f5;
                border-radius: 14px;
            }
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
            QPushButton:disabled {
                background: #94a3b8;
                color: #e2e8f0;
            }
            QFrame#sidebarCard QPushButton {
                text-align: right;
                background: transparent;
                color: #1e293b;
                border: 1px solid transparent;
            }
            QFrame#sidebarCard QPushButton:hover {
                background: #dbeafe;
                color: #1d4ed8;
            }
            QFrame#sidebarCard QPushButton:checked {
                background: #2563eb;
                color: white;
            }
            QHeaderView::section {
                background: #e2e8f0;
                border: none;
                padding: 10px;
                font-weight: 700;
            }
            """
        )

    def _handle_login(self, username: str, password: str) -> None:
        if not username or not password:
            self.login_page.show_error("کد دانشجویی و رمز عبور را وارد کنید.")
            return

        self.login_page.set_busy(True)
        self._set_busy(True)
        self.statusBar().showMessage("در حال برقراری ارتباط با سرور...")

        try:
            login_data = self.student_service.login(username=username, password=password)
            user = login_data.get("user") or {}
            if user.get("role") != "STUDENT":
                raise ApiError("این نسخه فقط برای دانشجوها فعال است.")

            token = login_data.get("token")
            if not token:
                raise ApiError("توکن ورود از سمت سرور دریافت نشد.")

            self.session.start(token=token, user=user)
            self.api_client.set_token(token)
            self.refresh_all_data()
            self.root_stack.setCurrentIndex(1)
            self._switch_page("dashboard")
            self.login_page.clear_form()
            self.statusBar().showMessage("ورود با موفقیت انجام شد.", 5000)
        except Exception as exc:
            self.session.clear()
            self.api_client.set_token(None)
            self.login_page.show_error(translate_error(exc))
            self.statusBar().showMessage("ورود انجام نشد.", 5000)
        finally:
            self._set_busy(False)
            self.login_page.set_busy(False)

    def refresh_all_data(self) -> None:
        if not self.session.is_authenticated:
            return

        self.statusBar().showMessage("در حال دریافت اطلاعات از سرور...")
        self._set_busy(True)

        try:
            profile = self.student_service.get_profile()
            reservations = self.student_service.get_my_reservations()
            schedules = self.student_service.get_upcoming_schedules()

            self.profile_data = profile
            self.reservations_data = reservations
            self.schedules_data = schedules

            self.dashboard_page.set_dashboard_data(profile, reservations)
            self.profile_page.set_profile(profile)
            self.reservations_page.set_reservations(reservations)
            self.schedules_page.set_schedules(schedules, self._load_schedule_pixmap)

            full_name = profile.get("full_name") or "دانشجو"
            student_code = profile.get("student_code") or "-"
            self.header_subtitle.setText(f"{full_name} | کد دانشجویی: {student_code}")
            self.statusBar().showMessage("اطلاعات با موفقیت به‌روزرسانی شد.", 5000)
        except Exception as exc:
            self._show_error_message("خطا", translate_error(exc))
            if isinstance(exc, ApiError) and exc.status_code == 401:
                self._logout(session_expired=True)
            self.statusBar().showMessage("به‌روزرسانی اطلاعات انجام نشد.", 5000)
        finally:
            self._set_busy(False)

    def _reserve_schedule(self, schedule: dict[str, Any]) -> None:
        meal_name = (schedule.get("meal") or {}).get("name", "غذا")
        schedule_date = format_date(schedule.get("date"))
        confirmed = self._confirm_action(
            "تایید رزرو",
            f"آیا از ثبت رزرو برای «{meal_name}» در تاریخ {schedule_date} مطمئن هستید؟",
        )
        if not confirmed:
            return

        try:
            self._set_busy(True)
            reservation = self.student_service.create_reservation(
                meal_schedule_id=int(schedule.get("id"))
            )
            reservation_code = reservation.get("reservation_code", "-")
            self._show_info_message(
                "رزرو ثبت شد",
                f"رزرو با موفقیت انجام شد.\nکد رزرو: {reservation_code}",
            )
            self.refresh_all_data()
        except Exception as exc:
            self._show_warning_message("خطا در رزرو", translate_error(exc))
            if isinstance(exc, ApiError) and exc.status_code == 401:
                self._logout(session_expired=True)
        finally:
            self._set_busy(False)

    def _cancel_reservation(self, reservation: dict[str, Any]) -> None:
        confirmed = self._confirm_action(
            "تایید لغو رزرو",
            f"آیا از لغو رزرو «{reservation.get('reservation_code', '-') }» مطمئن هستید؟",
        )
        if not confirmed:
            return

        try:
            self._set_busy(True)
            self.student_service.cancel_reservation(reservation_id=int(reservation.get("id")))
            self._show_info_message("رزرو لغو شد", "رزرو با موفقیت لغو شد.")
            self.refresh_all_data()
        except Exception as exc:
            self._show_warning_message("خطا در لغو رزرو", translate_error(exc))
            if isinstance(exc, ApiError) and exc.status_code == 401:
                self._logout(session_expired=True)
        finally:
            self._set_busy(False)

    def _logout(self, *, session_expired: bool = False) -> None:
        self.session.clear()
        self.api_client.set_token(None)
        self._reset_authenticated_state()
        self.root_stack.setCurrentIndex(0)
        self.login_page.clear_form()
        self.header_subtitle.setText("برای شروع وارد حساب دانشجویی خود شوید.")
        if session_expired:
            self.login_page.show_error("نشست شما منقضی شده است. لطفا دوباره وارد شوید.")
            self.statusBar().showMessage("نشست کاربری منقضی شد.", 5000)
        else:
            self.statusBar().showMessage("از حساب کاربری خارج شدید.", 5000)

    def _switch_page(self, page_key: str) -> None:
        mapping = {
            "dashboard": 0,
            "schedules": 1,
            "reservations": 2,
            "profile": 3,
        }
        page_index = mapping[page_key]
        self.page_stack.setCurrentIndex(page_index)

        for key, button in self.navigation_buttons.items():
            button.setChecked(key == page_key)

    def _load_schedule_pixmap(self, image_path: str | None) -> QPixmap | None:
        if not image_path:
            return None
        try:
            raw_bytes = self.api_client.fetch_binary(image_path)
        except Exception:
            return None

        pixmap = QPixmap()
        if pixmap.loadFromData(raw_bytes):
            return pixmap
        return None

    def _reset_authenticated_state(self) -> None:
        self.profile_data = {}
        self.reservations_data = []
        self.schedules_data = []
        self.dashboard_page.set_dashboard_data({}, [])
        self.profile_page.set_profile({})
        self.reservations_page.set_reservations([])
        self.schedules_page.set_schedules([], self._load_schedule_pixmap)
        self._switch_page("dashboard")

    def _set_busy(self, busy: bool) -> None:
        if busy and not self._busy_state:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self._busy_state = True
        elif not busy and self._busy_state:
            QApplication.restoreOverrideCursor()
            self._busy_state = False

    def _confirm_action(self, title: str, message: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setText(message)
        yes_button = dialog.addButton("بله", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton("انصراف", QMessageBox.ButtonRole.RejectRole)
        dialog.exec()
        return dialog.clickedButton() is yes_button

    def _show_info_message(self, title: str, message: str) -> None:
        self._show_message_box(title=title, message=message, icon=QMessageBox.Icon.Information)

    def _show_warning_message(self, title: str, message: str) -> None:
        self._show_message_box(title=title, message=message, icon=QMessageBox.Icon.Warning)

    def _show_error_message(self, title: str, message: str) -> None:
        self._show_message_box(title=title, message=message, icon=QMessageBox.Icon.Critical)

    def _show_message_box(self, *, title: str, message: str, icon: QMessageBox.Icon) -> None:
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setIcon(icon)
        dialog.setText(message)
        dialog.addButton("متوجه شدم", QMessageBox.ButtonRole.AcceptRole)
        dialog.exec()
