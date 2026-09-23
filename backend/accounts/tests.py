from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from test_helpers import create_admin_account, create_student_account


class AuthenticationApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_student_registration_creates_student_role_account(self) -> None:
        response = self.client.post(
            "/api/auth/student/register/",
            {
                "student_code": "40119999",
                "first_name": "Sara",
                "last_name": "Karimi",
                "phone_number": "09123334444",
                "password": "StrongPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student_code"], "40119999")
        self.assertEqual(response.data["user"]["role"], "STUDENT")

    def test_student_login_returns_token(self) -> None:
        create_student_account()

        response = self.client.post(
            "/api/auth/login/",
            {"username": "40110001", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["role"], "STUDENT")

    def test_admin_login_returns_admin_role(self) -> None:
        create_admin_account()

        response = self.client.post(
            "/api/auth/login/",
            {"username": "admin", "password": "AdminPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["role"], "ADMIN")
