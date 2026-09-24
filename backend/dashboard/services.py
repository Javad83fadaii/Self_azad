from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from meals.models import MealSchedule
from reservations.models import Reservation, ReservationStatus

OCCUPIED_STATUSES = [
    ReservationStatus.RESERVED,
    ReservationStatus.USED,
    ReservationStatus.NO_SHOW,
]


def resolve_dashboard_range(*, start_date=None, end_date=None):
    if end_date is None:
        end_date = timezone.localdate()
    if start_date is None:
        start_date = end_date - timedelta(days=29)
    return start_date, end_date


def get_dashboard_data(*, start_date=None, end_date=None) -> dict:
    start_date, end_date = resolve_dashboard_range(start_date=start_date, end_date=end_date)

    reservations_by_day = list(
        MealSchedule.objects.filter(date__range=(start_date, end_date))
        .values("date")
        .annotate(
            reservation_count=Count(
                "reservations",
                filter=Q(reservations__status__in=OCCUPIED_STATUSES),
            )
        )
        .order_by("date")
    )

    popular_meals = list(
        Reservation.objects.filter(
            meal_schedule__date__range=(start_date, end_date),
            status__in=OCCUPIED_STATUSES,
        )
        .annotate(
            meal_id=F("meal_schedule__meal_id"),
            meal_name=F("meal_schedule__meal__name"),
        )
        .values("meal_id", "meal_name")
        .annotate(total_reservations=Count("id"))
        .order_by("-total_reservations", "meal_name")
    )

    capacity_vs_reservations = []
    schedules = (
        MealSchedule.objects.select_related("meal")
        .filter(date__range=(start_date, end_date))
        .annotate(
            reservation_count=Count(
                "reservations",
                filter=Q(reservations__status__in=OCCUPIED_STATUSES),
            )
        )
        .order_by("date", "meal__name")
    )
    for schedule in schedules:
        capacity_vs_reservations.append(
            {
                "schedule_id": schedule.id,
                "date": schedule.date,
                "meal_id": schedule.meal_id,
                "meal_name": schedule.meal.name,
                "capacity": schedule.capacity,
                "reservation_count": schedule.reservation_count,
                "remaining_capacity": max(schedule.capacity - schedule.reservation_count, 0),
            }
        )

    daily_reservations = list(
        Reservation.objects.annotate(date=TruncDate("created_at"))
        .filter(date__range=(start_date, end_date))
        .values("date")
        .annotate(reservation_count=Count("id"))
        .order_by("date")
    )

    cancelled_reservations = list(
        Reservation.objects.filter(cancelled_at__isnull=False)
        .annotate(date=TruncDate("cancelled_at"))
        .filter(date__range=(start_date, end_date))
        .values("date")
        .annotate(cancelled_count=Count("id"))
        .order_by("date")
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "charts": {
            "reservations_by_day": reservations_by_day,
            "popular_meals": popular_meals,
            "capacity_vs_reservations": capacity_vs_reservations,
            "daily_reservations": daily_reservations,
            "cancelled_reservations": cancelled_reservations,
        },
    }
