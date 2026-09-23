from django.db import models
from django.db.models import Q

from common.models import CreatedUpdatedModel


class Meal(CreatedUpdatedModel):
    """Food item that can be offered to students."""

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, db_index=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="meals/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="meal_price_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class MealSchedule(CreatedUpdatedModel):
    """Meal availability for a specific calendar date."""

    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    date = models.DateField(db_index=True)
    capacity = models.PositiveIntegerField()
    reservation_open_at = models.DateTimeField()
    reservation_close_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["date", "meal__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["meal", "date"],
                name="unique_meal_schedule_per_day",
            ),
            models.CheckConstraint(
                condition=Q(capacity__gte=0),
                name="meal_schedule_capacity_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(reservation_open_at__lte=models.F("reservation_close_at")),
                name="meal_schedule_open_before_close",
            ),
        ]
        indexes = [
            models.Index(fields=["date"], name="meal_schedule_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.meal.name} - {self.date}"

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def reserved_count(self) -> int:
        return self.reservations.filter(status="RESERVED").count()

    @property
    def remaining_capacity(self) -> int:
        return max(self.capacity - self.reserved_count, 0)
