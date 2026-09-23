from __future__ import annotations

from typing import Any

from desktop.api.client import ApiError

ERROR_TRANSLATIONS = {
    "Invalid credentials.": "نام کاربری یا رمز عبور نادرست است.",
    "Authentication credentials were not provided.": "برای ادامه ابتدا وارد حساب کاربری خود شوید.",
    "Invalid token.": "نشست کاربری معتبر نیست. دوباره وارد شوید.",
    "User inactive or deleted.": "این حساب کاربری غیرفعال است.",
    "Duplicate reservation for this day is not allowed.": "برای این روز قبلا رزرو فعال ثبت شده است.",
    "Schedule capacity is full.": "ظرفیت این برنامه غذایی تکمیل شده است.",
    "Past schedules cannot be reserved.": "رزرو برای تاریخ گذشته مجاز نیست.",
    "Reservation is outside the allowed window.": "در حال حاضر بازه مجاز رزرو برای این غذا فعال نیست.",
    "Inactive schedules cannot be reserved.": "این برنامه غذایی غیرفعال است.",
    "Inactive meals cannot be reserved.": "این غذا غیرفعال است.",
    "Only active reservations can be cancelled.": "فقط رزروهای فعال قابل لغو هستند.",
    "This field is required.": "این فیلد الزامی است.",
}


def translate_error(error: Exception) -> str:
    if isinstance(error, ApiError):
        translated = _translate_payload(error.payload)
        if translated:
            return translated

        if error.message in ERROR_TRANSLATIONS:
            return ERROR_TRANSLATIONS[error.message]

        if error.status_code == 401:
            return "نشست شما منقضی شده است. لطفا دوباره وارد شوید."
        if error.status_code == 403:
            return "شما به این بخش دسترسی ندارید."
        if error.status_code == 404:
            return "اطلاعات موردنظر پیدا نشد."
        if error.status_code and error.status_code >= 500:
            return "در سمت سرور خطایی رخ داده است. لطفا دوباره تلاش کنید."
        return error.message

    return ERROR_TRANSLATIONS.get(str(error), str(error))


def _translate_payload(payload: Any) -> str | None:
    if payload is None:
        return None
    if isinstance(payload, str):
        return ERROR_TRANSLATIONS.get(payload, payload)
    if isinstance(payload, list):
        parts = [_translate_payload(item) for item in payload]
        normalized = [part for part in parts if part]
        return "، ".join(normalized) if normalized else None
    if isinstance(payload, dict):
        if payload.get("detail"):
            detail = str(payload["detail"])
            return ERROR_TRANSLATIONS.get(detail, detail)

        parts: list[str] = []
        for key, value in payload.items():
            translated_value = _translate_payload(value)
            if not translated_value:
                continue
            field_label = _translate_field_name(key)
            parts.append(f"{field_label}: {translated_value}" if field_label else translated_value)
        return " | ".join(parts) if parts else None
    return str(payload)


def _translate_field_name(field_name: str) -> str:
    field_labels = {
        "username": "نام کاربری",
        "password": "رمز عبور",
        "detail": "",
        "meal_schedule_id": "برنامه غذایی",
        "student_code": "کد دانشجویی",
        "phone_number": "شماره تماس",
    }
    return field_labels.get(field_name, field_name)
