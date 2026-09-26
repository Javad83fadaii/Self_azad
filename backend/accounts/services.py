from __future__ import annotations

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from accounts.models import User, UserRole
from students.models import Student

INVALID_LOGIN_MESSAGE = "اطلاعات ورود صحیح نیست."


def normalize_phone_number(phone_number: str) -> str:
    """Normalize Iranian mobile numbers for stable authentication checks."""
    digits = "".join(character for character in str(phone_number) if character.isdigit())
    if digits.startswith("0098"):
        digits = digits[4:]
    elif digits.startswith("98"):
        digits = digits[2:]
    if digits and not digits.startswith("0"):
        digits = f"0{digits}"
    return digits


@transaction.atomic
def register_student(*, student_code: str, first_name: str, last_name: str, phone_number: str, password: str) -> Student:
    if Student.objects.filter(student_code=student_code).exists():
        raise serializers.ValidationError({"student_code": "A student with this code already exists."})

    user = User.objects.create_user(
        username=student_code,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.STUDENT,
        is_active=True,
    )
    return Student.objects.create(
        user=user,
        student_code=student_code,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        is_active=True,
    )


def login_user(*, username: str, password: str) -> tuple[str, User]:
    user = authenticate(username=username, password=password)
    if user is None or not user.is_active:
        raise serializers.ValidationError({"detail": "Invalid credentials."})

    token, _ = Token.objects.get_or_create(user=user)
    return token.key, user


def login_student_for_web(*, student_code: str, phone_number: str) -> Student:
    normalized_student_code = student_code.strip()
    normalized_phone_number = normalize_phone_number(phone_number)

    try:
        student = Student.objects.select_related("user").get(student_code=normalized_student_code)
    except Student.DoesNotExist as exc:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE}) from exc

    if not student.is_active or not student.user.is_active:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})

    stored_phone_number = normalize_phone_number(student.phone_number)
    if stored_phone_number != normalized_phone_number:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})

    if student.user.role != UserRole.STUDENT:
        raise serializers.ValidationError({"detail": INVALID_LOGIN_MESSAGE})

    return student


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
