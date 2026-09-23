from django.conf import settings
from django.db import models

from common.models import CreatedUpdatedModel


class Student(CreatedUpdatedModel):
    """Student profile stored separately from authentication details."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    student_code = models.CharField(max_length=20, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["student_code"]
        indexes = [
            models.Index(fields=["phone_number"], name="student_phone_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.student_code} - {self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
