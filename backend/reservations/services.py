from __future__ import annotations

from uuid import uuid4

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from meals.models import MealSchedule
from reservations.models import Reservation, ReservationStatus
from students.models import Student


def _build_reservation_code() -> str:
    return f"RSV-{uuid4().hex[:12].upper()}"


def list_student_reservations(*, student: Student):
    return (
        Reservation.objects.select_related("student", "meal_schedule", "meal_schedule__meal")
        .filter(student=student)
        .order_by("-created_at")
    )


def list_admin_reservations(*, reservation_date=None, meal_id=None):
    queryset = Reservation.objects.select_related("student", "meal_schedule", "meal_schedule__meal").all()
    if reservation_date is not None:
        queryset = queryset.filter(reservation_date=reservation_date)
    if meal_id is not None:
        queryset = queryset.filter(meal_schedule__meal_id=meal_id)
    return queryset.order_by("-created_at")


@transaction.atomic
def create_reservation(*, student: Student, meal_schedule_id: int) -> Reservation:
    locked_student = Student.objects.select_for_update().get(pk=student.pk)
    schedule = get_object_or_404(
        MealSchedule.objects.select_for_update().select_related("meal"),
        pk=meal_schedule_id,
    )

    now = timezone.localtime(timezone.now())
    today = timezone.localdate()

    if not schedule.is_active:
        raise serializers.ValidationError({"meal_schedule_id": "Inactive schedules cannot be reserved."})
    if not schedule.meal.is_active:
        raise serializers.ValidationError({"meal_schedule_id": "Inactive meals cannot be reserved."})
    if schedule.date < today:
        raise serializers.ValidationError({"meal_schedule_id": "Past schedules cannot be reserved."})
    if now < schedule.reservation_open_at or now > schedule.reservation_close_at:
        raise serializers.ValidationError({"meal_schedule_id": "Reservation is outside the allowed window."})
    if Reservation.objects.filter(
        student=locked_student,
        reservation_date=schedule.date,
        status=ReservationStatus.RESERVED,
    ).exists():
        raise serializers.ValidationError({"detail": "Duplicate reservation for this day is not allowed."})

    reserved_count = Reservation.objects.filter(
        meal_schedule=schedule,
        status=ReservationStatus.RESERVED,
    ).count()
    if reserved_count >= schedule.capacity:
        raise serializers.ValidationError({"detail": "Schedule capacity is full."})

    try:
        return Reservation.objects.create(
            reservation_code=_build_reservation_code(),
            student=locked_student,
            meal_schedule=schedule,
            status=ReservationStatus.RESERVED,
        )
    except IntegrityError as exc:
        raise serializers.ValidationError({"detail": "Duplicate reservation for this day is not allowed."}) from exc


@transaction.atomic
def cancel_reservation(*, reservation: Reservation) -> Reservation:
    locked_reservation = Reservation.objects.select_for_update().select_related("meal_schedule").get(pk=reservation.pk)
    if locked_reservation.status != ReservationStatus.RESERVED:
        raise serializers.ValidationError({"detail": "Only active reservations can be cancelled."})

    locked_reservation.status = ReservationStatus.CANCELLED
    locked_reservation.cancelled_at = timezone.now()
    locked_reservation.save(update_fields=["status", "cancelled_at", "active_reservation_date"])
    return locked_reservation
