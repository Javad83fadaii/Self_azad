from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status

from reservations.models import Reservation, ReservationStatus
from test_helpers import (
    auth_client_for,
    create_admin_account,
    create_meal,
    create_schedule,
    create_student_account,
)


class ReservationApiTests(TestCase):
    def setUp(self) -> None:
        self.student_user, self.student = create_student_account()
        self.other_user, self.other_student = create_student_account(
            student_code="40110002",
            phone_number="09120000001",
        )
        self.admin_user = create_admin_account()
        self.student_client = auth_client_for(self.student_user)
        self.other_client = auth_client_for(self.other_user)
        self.admin_client = auth_client_for(self.admin_user)
        self.meal_one = create_meal(name="Ghormeh Sabzi", code="GHORMEH")
        self.meal_two = create_meal(name="Joojeh", code="JOOJEH")

    def test_create_reservation(self) -> None:
        schedule = create_schedule(meal=self.meal_one, capacity=2)

        response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], ReservationStatus.RESERVED)

    def test_duplicate_reservation(self) -> None:
        schedule_one = create_schedule(meal=self.meal_one, days_offset=2, capacity=2)
        schedule_two = create_schedule(meal=self.meal_two, days_offset=2, capacity=2)

        first_response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule_one.id},
            format="json",
        )
        second_response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule_two.id},
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Duplicate reservation", str(second_response.data["detail"]))

    def test_capacity_limit(self) -> None:
        schedule = create_schedule(meal=self.meal_one, capacity=1)

        first_response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )
        second_response = self.other_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("capacity is full", str(second_response.data["detail"]))

    def test_cancellation(self) -> None:
        schedule = create_schedule(meal=self.meal_one, capacity=2)
        create_response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )

        response = self.student_client.delete(f"/api/reservations/{create_response.data['id']}/cancel/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], ReservationStatus.CANCELLED)

    def test_student_can_reserve_again_after_cancellation(self) -> None:
        first_schedule = create_schedule(meal=self.meal_one, days_offset=2, capacity=2)
        second_schedule = create_schedule(meal=self.meal_two, days_offset=2, capacity=2)

        create_response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": first_schedule.id},
            format="json",
        )
        cancel_response = self.student_client.delete(f"/api/reservations/{create_response.data['id']}/cancel/")
        second_response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": second_schedule.id},
            format="json",
        )

        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.data["schedule_date"], second_schedule.date.isoformat())

    def test_student_cannot_cancel_other_students_reservation(self) -> None:
        schedule = create_schedule(meal=self.meal_one, capacity=2)
        create_response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )

        response = self.other_client.delete(f"/api/reservations/{create_response.data['id']}/cancel/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_past_date(self) -> None:
        schedule = create_schedule(
            meal=self.meal_one,
            days_offset=-1,
            open_offset_days=-3,
            close_offset_days=1,
        )

        response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Past schedules", str(response.data["meal_schedule_id"]))

    def test_reservation_window(self) -> None:
        schedule = create_schedule(
            meal=self.meal_one,
            days_offset=3,
            open_offset_days=1,
            close_offset_days=2,
        )

        response = self.student_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("allowed window", str(response.data["meal_schedule_id"]))

    def test_admin_can_list_reservations(self) -> None:
        schedule = create_schedule(meal=self.meal_one, capacity=2)
        Reservation.objects.create(
            reservation_code="RSV-ADMIN-01",
            student=self.student,
            meal_schedule=schedule,
            status=ReservationStatus.RESERVED,
        )

        response = self.admin_client.get("/api/admin/reservations/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_lists_only_own_reservations(self) -> None:
        my_schedule = create_schedule(meal=self.meal_one, capacity=3)
        other_schedule = create_schedule(meal=self.meal_two, days_offset=2, capacity=3)
        Reservation.objects.create(
            reservation_code="RSV-MINE-01",
            student=self.student,
            meal_schedule=my_schedule,
            status=ReservationStatus.RESERVED,
        )
        Reservation.objects.create(
            reservation_code="RSV-OTHER-01",
            student=self.other_student,
            meal_schedule=other_schedule,
            status=ReservationStatus.RESERVED,
        )

        response = self.student_client.get("/api/reservations/my/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student_code"], self.student.student_code)

    def test_admin_can_filter_reservations_by_date(self) -> None:
        target_schedule = create_schedule(meal=self.meal_one, days_offset=4, capacity=3)
        create_schedule(meal=self.meal_two, days_offset=5, capacity=3)
        Reservation.objects.create(
            reservation_code="RSV-DATE-01",
            student=self.student,
            meal_schedule=target_schedule,
            status=ReservationStatus.RESERVED,
        )

        response = self.admin_client.get(
            f"/api/admin/reservations/by-date/?date={target_schedule.date.isoformat()}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reservation_date"], target_schedule.date.isoformat())

    def test_admin_can_filter_reservations_by_meal(self) -> None:
        target_schedule = create_schedule(meal=self.meal_one, days_offset=4, capacity=3)
        other_schedule = create_schedule(meal=self.meal_two, days_offset=5, capacity=3)
        Reservation.objects.create(
            reservation_code="RSV-MEAL-01",
            student=self.student,
            meal_schedule=target_schedule,
            status=ReservationStatus.RESERVED,
        )
        Reservation.objects.create(
            reservation_code="RSV-MEAL-02",
            student=self.other_student,
            meal_schedule=other_schedule,
            status=ReservationStatus.RESERVED,
        )

        response = self.admin_client.get(f"/api/admin/reservations/by-meal/?meal_id={self.meal_one.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["meal_id"], self.meal_one.id)

    def test_database_constraint_blocks_duplicate_active_reservations_per_day(self) -> None:
        schedule_one = create_schedule(meal=self.meal_one, days_offset=6, capacity=3)
        schedule_two = create_schedule(meal=self.meal_two, days_offset=6, capacity=3)

        Reservation.objects.create(
            reservation_code="RSV-DB-01",
            student=self.student,
            meal_schedule=schedule_one,
            status=ReservationStatus.RESERVED,
        )

        with self.assertRaises(ValidationError):
            Reservation.objects.create(
                reservation_code="RSV-DB-02",
                student=self.student,
                meal_schedule=schedule_two,
                status=ReservationStatus.RESERVED,
            )
