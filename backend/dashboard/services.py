from __future__ import annotations

from collections import Counter
from datetime import datetime, time, timedelta

from django.db.models import Count, F, Q
from django.utils import timezone

from meals.models import MealSchedule
from reservations.models import Reservation, ReservationStatus
from students.models import Student

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
    current_tz = timezone.get_current_timezone()
    today = timezone.localdate()
    now = timezone.localtime(timezone.now())
    start_dt = timezone.make_aware(datetime.combine(start_date, time.min), current_tz)
    end_dt = timezone.make_aware(datetime.combine(end_date + timedelta(days=1), time.min), current_tz)

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

    daily_reservations_counts = Counter(
        timezone.localtime(created_at, current_tz).date()
        for created_at in Reservation.objects.filter(
            created_at__gte=start_dt,
            created_at__lt=end_dt,
        ).values_list("created_at", flat=True)
    )
    daily_reservations = [
        {"date": date, "reservation_count": daily_reservations_counts[date]}
        for date in sorted(daily_reservations_counts)
    ]

    cancelled_reservations_counts = Counter(
        timezone.localtime(cancelled_at, current_tz).date()
        for cancelled_at in Reservation.objects.filter(
            cancelled_at__isnull=False,
            cancelled_at__gte=start_dt,
            cancelled_at__lt=end_dt,
        ).values_list("cancelled_at", flat=True)
    )
    cancelled_reservations = [
        {"date": date, "cancelled_count": cancelled_reservations_counts[date]}
        for date in sorted(cancelled_reservations_counts)
    ]

    today_schedules = (
        MealSchedule.objects.select_related("meal")
        .filter(date=today)
        .annotate(
            reservation_count=Count(
                "reservations",
                filter=Q(reservations__status__in=OCCUPIED_STATUSES),
            )
        )
        .order_by("meal__name")
    )
    today_meals = []
    today_capacity_total = 0
    today_capacity_used = 0
    for schedule in today_schedules:
        remaining_capacity = max(schedule.capacity - schedule.reservation_count, 0)
        utilization_percentage = _calculate_utilization(
            reserved_count=schedule.reservation_count,
            capacity=schedule.capacity,
        )
        if not schedule.is_active or not schedule.meal.is_active:
            reservation_state = "INACTIVE"
        elif now < schedule.reservation_open_at:
            reservation_state = "NOT_OPEN"
        elif now > schedule.reservation_close_at:
            reservation_state = "CLOSED"
        elif remaining_capacity <= 0:
            reservation_state = "FULL"
        else:
            reservation_state = "AVAILABLE"

        today_capacity_total += schedule.capacity
        today_capacity_used += schedule.reservation_count
        today_meals.append(
            {
                "schedule_id": schedule.id,
                "date": schedule.date,
                "meal_id": schedule.meal_id,
                "meal_name": schedule.meal.name,
                "capacity": schedule.capacity,
                "reservation_count": schedule.reservation_count,
                "remaining_capacity": remaining_capacity,
                "utilization_percentage": utilization_percentage,
                "reservation_state": reservation_state,
                "is_active": schedule.is_active and schedule.meal.is_active,
            }
        )

    summary = {
        "total_students": Student.objects.filter(is_active=True).count(),
        "today_reservations": Reservation.objects.filter(
            meal_schedule__date=today,
            status__in=OCCUPIED_STATUSES,
        ).count(),
        "upcoming_reservations": Reservation.objects.filter(
            meal_schedule__date__gt=today,
            status=ReservationStatus.RESERVED,
        ).count(),
        "active_meals": MealSchedule.objects.filter(meal__is_active=True).values("meal_id").distinct().count(),
        "today_capacity_used": today_capacity_used,
        "today_capacity_remaining": max(today_capacity_total - today_capacity_used, 0),
    }

    status_distribution = [
        {
            "status": ReservationStatus.RESERVED,
            "count": Reservation.objects.filter(
                meal_schedule__date__range=(start_date, end_date),
                status=ReservationStatus.RESERVED,
            ).count(),
        },
        {
            "status": ReservationStatus.CANCELLED,
            "count": Reservation.objects.filter(
                meal_schedule__date__range=(start_date, end_date),
                status=ReservationStatus.CANCELLED,
            ).count(),
        },
        {
            "status": ReservationStatus.USED,
            "count": Reservation.objects.filter(
                meal_schedule__date__range=(start_date, end_date),
                status=ReservationStatus.USED,
            ).count(),
        },
        {
            "status": ReservationStatus.NO_SHOW,
            "count": Reservation.objects.filter(
                meal_schedule__date__range=(start_date, end_date),
                status=ReservationStatus.NO_SHOW,
            ).count(),
        },
    ]

    alerts = []
    if not today_meals:
        alerts.append(
            {
                "tone": "warning",
                "title": "برنامه امروز ثبت نشده است",
                "message": "برای امروز هیچ برنامه غذایی فعالی در سامانه وجود ندارد.",
            }
        )
    full_meals = [item["meal_name"] for item in today_meals if item["reservation_state"] == "FULL"]
    if full_meals:
        alerts.append(
            {
                "tone": "danger",
                "title": "تکمیل ظرفیت",
                "message": f"{len(full_meals)} غذا برای امروز تکمیل ظرفیت شده است.",
            }
        )
    if today_meals and summary["today_reservations"] == 0:
        alerts.append(
            {
                "tone": "info",
                "title": "رزروی برای امروز ثبت نشده است",
                "message": "برای برنامه امروز هنوز رزرو فعالی ثبت نشده است.",
            }
        )

    return {
        "current_date": today,
        "start_date": start_date,
        "end_date": end_date,
        "summary": summary,
        "today_meals": today_meals,
        "alerts": alerts,
        "charts": {
            "reservations_by_day": reservations_by_day,
            "popular_meals": popular_meals,
            "capacity_vs_reservations": capacity_vs_reservations,
            "daily_reservations": daily_reservations,
            "cancelled_reservations": cancelled_reservations,
            "status_distribution": status_distribution,
        },
    }


def _calculate_utilization(*, reserved_count: int, capacity: int) -> float:
    if capacity <= 0:
        return 0.0
    return round((reserved_count / capacity) * 100, 2)
