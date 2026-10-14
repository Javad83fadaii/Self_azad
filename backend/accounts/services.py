from __future__ import annotations

from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from rest_framework import serializers

from accounts.models import User, UserRole
from students.models import Student

INVALID_LOGIN_MESSAGE = "اطلاعات ورود صحیح نیست."
PROFILE_COMPLETION_MESSAGE = "برای اولین ورود، نام و نام خانوادگی را هم وارد کنید."
PERSIAN_DIGIT_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(value: str) -> str:
    """Convert Persian and Arabic digits to ASCII digits."""
    return str(value or "").translate(PERSIAN_DIGIT_TRANSLATION)


def normalize_student_code(student_code: str) -> str:
    """Normalize the student code for consistent lookups."""
    return normalize_digits(student_code).strip()


def normalize_name(value: str | None) -> str:
    """Trim optional profile fields."""
    return str(value or "").strip()


def normalize_phone_number(phone_number: str) -> str:
    """Normalize Iranian mobile numbers for stable authentication checks."""
    digits = "".join(character for character in normalize_digits(phone_number) if character.isdigit())
    if digits.startswith("0098"):
        digits = digits[4:]
    elif digits.startswith("98"):
        digits = digits[2:]
    if digits and not digits.startswith("0"):
        digits = f"0{digits}"
    return digits


@transaction.atomic
def provision_student_for_web(*, student_code: str, first_name: str, last_name: str, phone_number: str) -> Student:
    normalized_student_code = normalize_student_code(student_code)
    normalized_phone_number = normalize_phone_number(phone_number)
    normalized_first_name = normalize_name(first_name)
    normalized_last_name = normalize_name(last_name)

    if Student.objects.filter(student_code=normalized_student_code).exists():
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})
    if User.objects.filter(username=normalized_student_code).exists():
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})

    try:
        user = User.objects.create_user(
            username=normalized_student_code,
            password=None,
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            role=UserRole.STUDENT,
            is_active=True,
        )
        return Student.objects.create(
            user=user,
            student_code=normalized_student_code,
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            phone_number=normalized_phone_number,
            is_active=True,
        )
    except IntegrityError as exc:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE}) from exc


def student_profile_is_complete(student: Student) -> bool:
    """Check whether both the student profile and user names are populated."""
    return all(
        [
            normalize_name(student.first_name),
            normalize_name(student.last_name),
            normalize_name(student.user.first_name),
            normalize_name(student.user.last_name),
        ]
    )


@transaction.atomic
def complete_student_profile_for_web(*, student: Student, first_name: str, last_name: str) -> Student:
    normalized_first_name = normalize_name(first_name)
    normalized_last_name = normalize_name(last_name)

    student = Student.objects.select_for_update().select_related("user").get(pk=student.pk)
    student.first_name = normalized_first_name
    student.last_name = normalized_last_name
    student.user.first_name = normalized_first_name
    student.user.last_name = normalized_last_name
    student.user.save(update_fields=["first_name", "last_name"])
    student.save(update_fields=["first_name", "last_name", "updated_at"])
    return student


def login_student_for_web(
    *,
    student_code: str,
    phone_number: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> Student:
    normalized_student_code = normalize_student_code(student_code)
    normalized_phone_number = normalize_phone_number(phone_number)
    normalized_first_name = normalize_name(first_name)
    normalized_last_name = normalize_name(last_name)

    has_profile_names = bool(normalized_first_name and normalized_last_name)

    try:
        student = Student.objects.select_related("user").get(student_code=normalized_student_code)
    except Student.DoesNotExist:
        if not has_profile_names:
            raise serializers.ValidationError(
                {
                    "detail": PROFILE_COMPLETION_MESSAGE,
                    "requires_profile_completion": True,
                }
            )
        return provision_student_for_web(
            student_code=normalized_student_code,
            first_name=normalized_first_name,
            last_name=normalized_last_name,
            phone_number=normalized_phone_number,
        )

    if not student.is_active or not student.user.is_active:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})

    stored_phone_number = normalize_phone_number(student.phone_number)
    if stored_phone_number != normalized_phone_number:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})

    if student.user.role != UserRole.STUDENT:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})

    if not student_profile_is_complete(student):
        if not has_profile_names:
            raise serializers.ValidationError(
                {
                    "detail": PROFILE_COMPLETION_MESSAGE,
                    "requires_profile_completion": True,
                }
            )
        return complete_student_profile_for_web(
            student=student,
            first_name=normalized_first_name,
            last_name=normalized_last_name,
        )

    return student


def login_admin_for_web(*, username: str, password: str) -> User:
    user = authenticate(username=username.strip(), password=password)
    if user is None or not user.is_active or user.role != UserRole.ADMIN:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})
    return user


def build_current_user_payload(*, user: User) -> dict[str, object]:
    student_profile = getattr(user, "student_profile", None)
    payload: dict[str, object] = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
    }

    if student_profile is not None:
        payload.update(
            {
                "student_id": student_profile.id,
                "student_code": student_profile.student_code,
                "phone": student_profile.phone_number,
            }
        )

    return payload
