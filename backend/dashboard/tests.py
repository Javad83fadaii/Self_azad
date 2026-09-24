from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from reservations.models import Reservation, ReservationStatus
from test_helpers import (
    auth_client_for,
    create_admin_account,
    create_meal,
    create_schedule,
    create_student_account,
)


class DashboardApiTests(TestCase):
    def setUp(self) -> None:
        self.admin_user = create_admin_account()
        self.student_user, self.student = create_student_account()
        self.other_user, self.other_student = create_student_account(
            student_code="40110002",
            phone_number="09120000001",
        )
        self.admin_client = auth_client_for(self.admin_user)
        self.student_client = auth_client_for(self.student_user)

        self.meal_one = create_meal(name="Ghormeh Sabzi", code="GHORMEH")
        self.meal_two = create_meal(name="Joojeh", code="JOOJEH")
        self.schedule_one = create_schedule(meal=self.meal_one, days_offset=1, capacity=5)
        self.schedule_two = create_schedule(meal=self.meal_two, days_offset=2, capacity=3)

        now = timezone.now()
        self.reserved = Reservation.objects.create(
            reservation_code="RSV-DSH-01",
            student=self.student,
            meal_schedule=self.schedule_one,
            status=ReservationStatus.RESERVED,
        )
        self.used = Reservation.objects.create(
            reservation_code="RSV-DSH-02",
            student=self.other_student,
            meal_schedule=self.schedule_one,
            status=ReservationStatus.USED,
        )
        self.cancelled = Reservation.objects.create(
            reservation_code="RSV-DSH-03",
            student=self.other_student,
            meal_schedule=self.schedule_two,
            status=ReservationStatus.CANCELLED,
        )

        Reservation.objects.filter(pk=self.reserved.pk).update(created_at=now - timedelta(days=1))
        Reservation.objects.filter(pk=self.used.pk).update(created_at=now)
        Reservation.objects.filter(pk=self.cancelled.pk).update(
            created_at=now,
            cancelled_at=now,
        )

    def test_admin_can_get_dashboard_datasets(self) -> None:
        response = self.admin_client.get(
            "/api/admin/dashboard/",
            {
                "start_date": timezone.localdate().isoformat(),
                "end_date": (timezone.localdate() + timedelta(days=3)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_date"], timezone.localdate().isoformat())
        self.assertIn("charts", response.data)
        self.assertEqual(len(response.data["charts"]["capacity_vs_reservations"]), 2)
        self.assertEqual(response.data["charts"]["popular_meals"][0]["meal_name"], "Ghormeh Sabzi")
        self.assertEqual(response.data["charts"]["popular_meals"][0]["total_reservations"], 2)
        self.assertEqual(response.data["charts"]["reservations_by_day"][0]["reservation_count"], 2)
        self.assertEqual(response.data["charts"]["cancelled_reservations"][0]["cancelled_count"], 1)

    def test_student_cannot_access_dashboard(self) -> None:
        response = self.student_client.get("/api/admin/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
