from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import User, UserRole
from meals.models import Meal, MealSchedule
from students.models import Student


def create_student_account(
    *,
    student_code: str = "40110001",
    password: str = "StrongPass123",
    first_name: str = "Ali",
    last_name: str = "Ahmadi",
    phone_number: str = "09120000000",
) -> tuple[User, Student]:
    user = User.objects.create_user(
        username=student_code,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.STUDENT,
    )
    student = Student.objects.create(
        user=user,
        student_code=student_code,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        is_active=True,
    )
    return user, student


def create_admin_account(*, username: str = "admin", password: str = "AdminPass123") -> User:
    return User.objects.create_user(
        username=username,
        password=password,
        role=UserRole.ADMIN,
        is_staff=True,
    )


def auth_client_for(user: User) -> APIClient:
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


def create_meal(*, name: str = "Ghormeh Sabzi", code: str = "GHORMEH", is_active: bool = True) -> Meal:
    return Meal.objects.create(
        name=name,
        code=code,
        description=f"{name} meal",
        price="85000.00",
        is_active=is_active,
    )


def create_schedule(
    *,
    meal: Meal,
    days_offset: int = 1,
    capacity: int = 10,
    is_active: bool = True,
    open_offset_days: int = -1,
    close_offset_days: int = 1,
) -> MealSchedule:
    now = timezone.now()
    return MealSchedule.objects.create(
        meal=meal,
        date=timezone.localdate() + timedelta(days=days_offset),
        capacity=capacity,
        reservation_open_at=now + timedelta(days=open_offset_days),
        reservation_close_at=now + timedelta(days=close_offset_days),
        is_active=is_active,
    )
