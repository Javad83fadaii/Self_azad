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


class ReportsApiTests(TestCase):
    def setUp(self) -> None:
        self.admin_user = create_admin_account()
        self.student_user, self.student = create_student_account()
        self.other_user, self.other_student = create_student_account(
            student_code="40110002",
            first_name="Sara",
            last_name="Karimi",
            phone_number="09123334444",
        )
        self.admin_client = auth_client_for(self.admin_user)
        self.student_client = auth_client_for(self.student_user)

        self.meal_one = create_meal(name="Ghormeh Sabzi", code="GHORMEH")
        self.meal_two = create_meal(name="Joojeh", code="JOOJEH")
        self.schedule_one = create_schedule(meal=self.meal_one, days_offset=1, capacity=10)
        self.schedule_two = create_schedule(meal=self.meal_two, days_offset=1, capacity=8)
        self.schedule_three = create_schedule(meal=self.meal_one, days_offset=2, capacity=12)

        Reservation.objects.create(
            reservation_code="RSV-RPT-01",
            student=self.student,
            meal_schedule=self.schedule_one,
            status=ReservationStatus.RESERVED,
        )
        Reservation.objects.create(
            reservation_code="RSV-RPT-02",
            student=self.other_student,
            meal_schedule=self.schedule_one,
            status=ReservationStatus.CANCELLED,
        )
        Reservation.objects.create(
            reservation_code="RSV-RPT-03",
            student=self.other_student,
            meal_schedule=self.schedule_two,
            status=ReservationStatus.USED,
        )
        Reservation.objects.create(
            reservation_code="RSV-RPT-04",
            student=self.student,
            meal_schedule=self.schedule_three,
            status=ReservationStatus.NO_SHOW,
        )

    def test_admin_can_get_daily_meal_report(self) -> None:
        response = self.admin_client.get(
            "/api/admin/reports/daily-meals/",
            {"date": self.schedule_one.date.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["date"], self.schedule_one.date.isoformat())
        self.assertEqual(len(response.data["results"]), 2)
        first_row = response.data["results"][0]
        self.assertIn("reservation_count", first_row)
        self.assertIn("remaining_capacity", first_row)

    def test_student_report_filters_by_student_fields(self) -> None:
        response = self.admin_client.get(
            "/api/admin/reports/students/",
            {"first_name": "Sar", "phone_number": "3444"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["student_code"], "40110002")
        self.assertEqual(response.data["results"][0]["used_count"], 1)

    def test_meal_report_returns_aggregated_statuses(self) -> None:
        response = self.admin_client.get("/api/admin/reports/meals/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        ghormeh = next(item for item in response.data["results"] if item["meal_code"] == "GHORMEH")
        self.assertEqual(ghormeh["total_reservations"], 3)
        self.assertEqual(ghormeh["cancelled_count"], 1)
        self.assertEqual(ghormeh["no_show_count"], 1)
        self.assertEqual(ghormeh["capacity"], 22)

    def test_daily_meal_report_supports_csv_export(self) -> None:
        response = self.admin_client.get(
            "/api/admin/reports/daily-meals/",
            {"date": self.schedule_one.date.isoformat(), "export": "csv"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("daily_meal_report_", response["Content-Disposition"])

    def test_meal_report_supports_excel_export(self) -> None:
        response = self.admin_client.get("/api/admin/reports/meals/?export=xlsx")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_student_report_supports_pdf_export(self) -> None:
        response = self.admin_client.get("/api/admin/reports/students/?export=pdf")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_student_cannot_access_admin_reports(self) -> None:
        response = self.student_client.get("/api/admin/reports/meals/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
