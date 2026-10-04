from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserRole
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

    def test_admin_can_create_student_with_session_authentication(self) -> None:
        session_client = APIClient()
        session_client.force_login(self.admin_user)

        response = session_client.post(
            "/api/admin/students/",
            data={
                "student_code": "40112222",
                "first_name": "Mina",
                "last_name": "Karimi",
                "phone_number": "09123334455",
                "password": "StrongPass123",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student_code"], "40112222")
        self.assertEqual(response.data["username"], "40112222")
        self.assertEqual(response.data["role"], UserRole.STUDENT)
        created_user = User.objects.get(username="40112222")
        self.assertTrue(created_user.check_password("StrongPass123"))
        self.assertEqual(created_user.student_profile.phone_number, "09123334455")

    def test_student_cannot_create_student_from_admin_endpoint(self) -> None:
        session_client = APIClient()
        session_client.force_login(self.student_user)

        response = session_client.post(
            "/api/admin/students/",
            data={
                "student_code": "40113333",
                "first_name": "Niloofar",
                "last_name": "Jafari",
                "phone_number": "09125556688",
                "password": "StrongPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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


class StudentAdminTests(TestCase):
    def setUp(self) -> None:
        self.superuser = User.objects.create_superuser(
            username="rootadmin",
            password="RootAdmin123",
        )
        self.client.force_login(self.superuser)

    def test_admin_can_create_student_from_django_admin(self) -> None:
        response = self.client.post(
            reverse("admin:students_student_add"),
            data={
                "student_code": "40119999",
                "first_name": "Reza",
                "last_name": "Moradi",
                "phone_number": "09125556677",
                "is_active": "on",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        created_student = User.objects.get(username="40119999").student_profile
        self.assertEqual(created_student.first_name, "Reza")
        self.assertEqual(created_student.last_name, "Moradi")
        self.assertEqual(created_student.phone_number, "09125556677")
        self.assertTrue(created_student.is_active)
        self.assertEqual(created_student.user.role, UserRole.STUDENT)
        self.assertTrue(created_student.user.check_password("StrongPass123"))

    def test_admin_change_keeps_student_user_in_sync(self) -> None:
        student_user, student = create_student_account(
            student_code="40115555",
            first_name="Ali",
            last_name="Ahmadi",
            phone_number="09120001111",
        )

        response = self.client.post(
            reverse("admin:students_student_change", args=[student.pk]),
            data={
                "user": student_user.pk,
                "student_code": "40116666",
                "first_name": "Hossein",
                "last_name": "Karimi",
                "phone_number": "09129998877",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        student.refresh_from_db()
        student_user.refresh_from_db()

        self.assertEqual(student.student_code, "40116666")
        self.assertEqual(student.first_name, "Hossein")
        self.assertEqual(student.last_name, "Karimi")
        self.assertEqual(student.phone_number, "09129998877")
        self.assertFalse(student.is_active)
        self.assertEqual(student_user.username, "40116666")
        self.assertEqual(student_user.first_name, "Hossein")
        self.assertEqual(student_user.last_name, "Karimi")
        self.assertFalse(student_user.is_active)
