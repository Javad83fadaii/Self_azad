from __future__ import annotations

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from accounts.models import User, UserRole
from students.models import Student


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
