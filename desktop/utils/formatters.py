from __future__ import annotations

from datetime import date, datetime
from typing import Any


RESERVATION_STATUS_LABELS = {
    "RESERVED": "فعال",
    "CANCELLED": "لغوشده",
    "USED": "استفاده‌شده",
    "NO_SHOW": "عدم مراجعه",
}


def format_date(value: str | None) -> str:
    parsed_value = parse_date(value)
    if not parsed_value:
        return value or "-"
    return parsed_value.strftime("%Y/%m/%d")


def format_datetime(value: str | None) -> str:
    if not value:
        return "-"
    normalized_value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized_value).strftime("%Y/%m/%d - %H:%M")
    except ValueError:
        return value


def format_reservation_status(status: str | None) -> str:
    if not status:
        return "-"
    return RESERVATION_STATUS_LABELS.get(status, status)


def build_last_reservation_text(reservation: dict[str, Any] | None) -> str:
    if not reservation:
        return "هنوز رزروی ثبت نشده است."
    return (
        f"{reservation.get('meal_name', '-')}"
        f" | {format_date(reservation.get('schedule_date') or reservation.get('reservation_date'))}"
        f" | {format_reservation_status(reservation.get('status'))}"
    )


def build_schedule_status(schedule: dict[str, Any]) -> str:
    return get_schedule_status_meta(schedule)["label"]


def is_schedule_reservable(schedule: dict[str, Any]) -> bool:
    return bool(get_schedule_status_meta(schedule)["reservable"])


def is_future_active_reservation(
    reservation: dict[str, Any],
    *,
    reference_date: date | None = None,
) -> bool:
    schedule_day = parse_date(reservation.get("schedule_date") or reservation.get("reservation_date"))
    if not schedule_day:
        return False
    return reservation.get("status") == "RESERVED" and schedule_day >= (reference_date or date.today())


def format_schedule_day_heading(value: str | None) -> str:
    parsed_value = parse_date(value)
    if not parsed_value:
        return value or "-"
    weekday_labels = {
        0: "دوشنبه",
        1: "سه‌شنبه",
        2: "چهارشنبه",
        3: "پنج‌شنبه",
        4: "جمعه",
        5: "شنبه",
        6: "یکشنبه",
    }
    weekday_label = weekday_labels.get(parsed_value.weekday(), "")
    return f"{weekday_label} | {parsed_value.strftime('%Y/%m/%d')}"


def get_schedule_status_meta(schedule: dict[str, Any]) -> dict[str, Any]:
    meal = schedule.get("meal") or {}
    if not schedule.get("is_active", False) or not meal.get("is_active", False):
        return {"label": "غیرفعال", "reservable": False}
    if int(schedule.get("remaining_capacity") or 0) <= 0:
        return {"label": "تکمیل ظرفیت", "reservable": False}

    now = datetime.now().astimezone()
    open_at = _parse_datetime(schedule.get("reservation_open_at"))
    close_at = _parse_datetime(schedule.get("reservation_close_at"))

    if open_at and now < open_at:
        return {"label": "رزرو هنوز شروع نشده", "reservable": False}
    if close_at and now > close_at:
        return {"label": "مهلت رزرو تمام شده", "reservable": False}
    return {"label": "قابل رزرو", "reservable": True}


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
