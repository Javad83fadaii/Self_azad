from django.db import transaction

from accounts.models import User, UserRole
from students.models import Student


@transaction.atomic
def create_student(
    *,
    student_code: str,
    first_name: str,
    last_name: str,
    phone_number: str,
    password: str,
    is_active: bool = True,
) -> Student:
    user = User.objects.create_user(
        username=student_code,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.STUDENT,
        is_active=is_active,
    )
    return Student.objects.create(
        user=user,
        student_code=student_code,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        is_active=is_active,
    )


def get_student_profile(*, user) -> Student:
    return Student.objects.select_related("user").get(user=user)


def list_students():
    return Student.objects.select_related("user").order_by("student_code")
