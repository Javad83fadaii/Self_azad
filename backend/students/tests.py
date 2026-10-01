from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from test_helpers import auth_client_for, create_admin_account, create_student_account


class StudentPermissionApiTests(TestCase):
    def setUp(self) -> None:
        self.student_user, self.student = create_student_account()
        self.admin_user = create_admin_account()
        self.student_client = auth_client_for(self.student_user)
        self.admin_client = auth_client_for(self.admin_user)

    def test_student_can_view_own_profile(self) -> None:
        response = self.student_client.get("/api/students/me/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_code"], self.student.student_code)

    def test_student_cannot_access_admin_reservation_list(self) -> None:
        response = self.student_client.get("/api/admin/reservations/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_access_admin_student_list(self) -> None:
        response = self.student_client.get("/api/admin/students/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_access_student_only_profile_endpoint(self) -> None:
        response = self.admin_client.get("/api/students/me/profile/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_view_own_profile_with_session_authentication(self) -> None:
        session_client = APIClient()
        session_client.force_login(self.student_user)

        response = session_client.get("/api/students/me/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_code"], self.student.student_code)

    def test_admin_can_access_student_list_with_session_authentication(self) -> None:
        session_client = APIClient()
        session_client.force_login(self.admin_user)

        response = session_client.get("/api/admin/students/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class StudentModelValidationTests(TestCase):
    def test_student_profile_cannot_link_to_admin_user(self) -> None:
        admin_user = create_admin_account()
        _, existing_student = create_student_account(student_code="40110002", phone_number="09120000001")

        invalid_student = existing_student.__class__(
            user=admin_user,
            student_code="40110003",
            first_name="Sara",
            last_name="Karimi",
            phone_number="09123334444",
            is_active=True,
        )

        with self.assertRaises(ValidationError) as exc_info:
            invalid_student.full_clean()

        self.assertIn("user", exc_info.exception.message_dict)
