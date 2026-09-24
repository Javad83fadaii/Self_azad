from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from meals.models import MealSchedule
from students.models import Student


class ReservationStatus(models.TextChoices):
    RESERVED = "RESERVED", "Reserved"
    CANCELLED = "CANCELLED", "Cancelled"
    USED = "USED", "Used"
    NO_SHOW = "NO_SHOW", "No Show"


class Reservation(models.Model):
    """Reservation for a student's meal on a specific date."""

    reservation_code = models.CharField(max_length=32, unique=True, db_index=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    meal_schedule = models.ForeignKey(
        MealSchedule,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    reservation_date = models.DateField(editable=False, db_index=True)
    active_reservation_date = models.DateField(
        editable=False,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=16,
        choices=ReservationStatus.choices,
        default=ReservationStatus.RESERVED,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "active_reservation_date"],
                name="unique_active_student_reservation_date",
            ),
        ]
        indexes = [
            models.Index(fields=["status"], name="reservation_status_idx"),
            models.Index(fields=["meal_schedule", "status"], name="rsv_sched_status_idx"),
            models.Index(fields=["student", "reservation_date"], name="reservation_student_date_idx"),
        ]

    def clean(self) -> None:
        if self.meal_schedule_id:
            schedule_date = self.meal_schedule.date
            if self.reservation_date and self.reservation_date != schedule_date:
                raise ValidationError(
                    {"reservation_date": "Reservation date must match meal schedule date."}
                )

    def save(self, *args, **kwargs) -> None:
        if self.meal_schedule_id:
            self.reservation_date = self.meal_schedule.date
        self.active_reservation_date = (
            self.reservation_date if self.status == ReservationStatus.RESERVED else None
        )
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.reservation_code} - {self.student.student_code}"
