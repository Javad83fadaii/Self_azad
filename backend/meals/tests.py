from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from test_helpers import auth_client_for, create_admin_account, create_meal, create_schedule, create_student_account


class MealAdminPermissionApiTests(TestCase):
    def setUp(self) -> None:
        self.student_user, _ = create_student_account()
        self.admin_user = create_admin_account()
        self.student_client = auth_client_for(self.student_user)
        self.admin_client = auth_client_for(self.admin_user)

    def test_student_cannot_create_meal(self) -> None:
        response = self.student_client.post(
            "/api/meals/",
            {
                "name": "Kotlet",
                "code": "KOTLET",
                "description": "Admin only",
                "price": "70000.00",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_create_schedule(self) -> None:
        meal = create_meal()

        response = self.student_client.post(
            "/api/schedules/",
            {
                "meal_id": meal.id,
                "date": "2030-01-05",
                "capacity": 50,
                "reservation_open_at": "2030-01-01T08:00:00+03:30",
                "reservation_close_at": "2030-01-03T18:00:00+03:30",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_and_update_meal(self) -> None:
        create_response = self.admin_client.post(
            "/api/meals/",
            {
                "name": "Kotlet",
                "code": "KOTLET",
                "description": "Admin only",
                "price": "70000.00",
                "is_active": True,
            },
            format="json",
        )
        meal_id = create_response.data["id"]
        update_response = self.admin_client.put(
            f"/api/meals/{meal_id}/",
            {
                "name": "Kotlet Updated",
                "code": "KOTLET",
                "description": "Updated",
                "price": "75000.00",
                "is_active": True,
                "image": None,
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "Kotlet Updated")

    def test_admin_can_list_meals_and_schedules_from_admin_namespace(self) -> None:
        meal = create_meal()
        create_schedule(meal=meal, capacity=10)

        meals_response = self.admin_client.get("/api/admin/meals/")
        schedules_response = self.admin_client.get("/api/admin/schedules/")

        self.assertEqual(meals_response.status_code, status.HTTP_200_OK)
        self.assertEqual(schedules_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(meals_response.data), 1)
        self.assertEqual(len(schedules_response.data), 1)

    def test_student_cannot_access_admin_meal_list(self) -> None:
        response = self.student_client.get("/api/admin/meals/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_deactivate_meal(self) -> None:
        meal = create_meal()

        delete_response = self.admin_client.delete(f"/api/meals/{meal.id}/")
        meal.refresh_from_db()

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(meal.is_active)

    def test_admin_can_update_schedule(self) -> None:
        meal = create_meal()
        schedule = create_schedule(meal=meal, capacity=10)

        response = self.admin_client.put(
            f"/api/schedules/{schedule.id}/",
            {
                "meal_id": meal.id,
                "date": schedule.date.isoformat(),
                "capacity": 42,
                "reservation_open_at": schedule.reservation_open_at.isoformat(),
                "reservation_close_at": schedule.reservation_close_at.isoformat(),
                "is_active": True,
            },
            format="json",
        )
        schedule.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["capacity"], 42)
        self.assertEqual(schedule.capacity, 42)

    def test_admin_can_create_and_deactivate_schedule(self) -> None:
        meal = create_meal()
        future_date = timezone.localdate() + timedelta(days=5)
        create_response = self.admin_client.post(
            "/api/schedules/",
            {
                "meal_id": meal.id,
                "date": future_date.isoformat(),
                "capacity": 50,
                "reservation_open_at": "2030-01-01T08:00:00+03:30",
                "reservation_close_at": "2030-01-02T18:00:00+03:30",
                "is_active": True,
            },
            format="json",
        )
        schedule_id = create_response.data["id"]
        delete_response = self.admin_client.delete(f"/api/schedules/{schedule_id}/")

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)


class StudentUpcomingScheduleApiTests(TestCase):
    def setUp(self) -> None:
        self.student_user, _ = create_student_account()
        self.student_client = auth_client_for(self.student_user)
        self.meal = create_meal(name="Adas Polo", code="ADAS")

    def test_student_can_view_upcoming_schedules(self) -> None:
        schedule = create_schedule(meal=self.meal, capacity=25)

        response = self.student_client.get("/api/schedules/upcoming/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], schedule.id)
        self.assertEqual(response.data[0]["capacity"], 25)
        self.assertEqual(response.data[0]["reservation_state"], "AVAILABLE")
        self.assertTrue(response.data[0]["is_reservable"])

    def test_upcoming_schedule_requires_authentication(self) -> None:
        response = self.client.get("/api/schedules/upcoming/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
