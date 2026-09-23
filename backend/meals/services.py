from __future__ import annotations

from django.db.models import Count, F, IntegerField, Q, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import serializers

from meals.models import Meal, MealSchedule
from reservations.models import ReservationStatus


def list_meals(*, active_only: bool = False):
    queryset = Meal.objects.all()
    if active_only:
        queryset = queryset.filter(is_active=True)
    return queryset.order_by("name")


def create_meal(**validated_data) -> Meal:
    meal = Meal(**validated_data)
    meal.save()
    return meal


def update_meal(*, meal: Meal, **validated_data) -> Meal:
    for field, value in validated_data.items():
        setattr(meal, field, value)
    meal.save()
    return meal


def deactivate_meal(*, meal: Meal) -> Meal:
    meal.is_active = False
    meal.save(update_fields=["is_active", "updated_at"])
    return meal


def _schedule_queryset():
    return MealSchedule.objects.select_related("meal").annotate(
        _reserved_count=Count(
            "reservations",
            filter=Q(reservations__status=ReservationStatus.RESERVED),
        ),
        _remaining_capacity=Coalesce(F("capacity"), Value(0), output_field=IntegerField())
        - Count(
            "reservations",
            filter=Q(reservations__status=ReservationStatus.RESERVED),
        ),
    )


def list_upcoming_schedules():
    today = timezone.localdate()
    return (
        _schedule_queryset()
        .filter(date__gte=today, is_active=True, meal__is_active=True)
        .order_by("date", "meal__name")
    )


def create_schedule(**validated_data) -> MealSchedule:
    meal = validated_data["meal"]
    if not meal.is_active:
        raise serializers.ValidationError({"meal_id": "Inactive meals cannot receive schedules."})
    schedule = MealSchedule(**validated_data)
    schedule.save()
    return schedule


def update_schedule(*, schedule: MealSchedule, **validated_data) -> MealSchedule:
    if "meal" in validated_data and not validated_data["meal"].is_active:
        raise serializers.ValidationError({"meal_id": "Inactive meals cannot receive schedules."})
    for field, value in validated_data.items():
        setattr(schedule, field, value)
    schedule.save()
    return schedule


def deactivate_schedule(*, schedule: MealSchedule) -> MealSchedule:
    schedule.is_active = False
    schedule.save(update_fields=["is_active", "updated_at"])
    return schedule
