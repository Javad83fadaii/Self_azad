from __future__ import annotations

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    STUDENT = "STUDENT", "Student"


class AccountUserManager(UserManager):
    """Custom manager that assigns a sensible default role."""

    def create_user(self, username: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("role", UserRole.STUDENT)
        return super().create_user(username=username, password=password, **extra_fields)

    def create_superuser(self, username: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return super().create_superuser(username=username, password=password, **extra_fields)


class User(AbstractUser):
    """Project user with API role information."""

    role = models.CharField(
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        db_index=True,
    )

    objects = AccountUserManager()

    class Meta:
        ordering = ["username"]

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
