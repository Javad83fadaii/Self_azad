from django.test import TestCase
from rest_framework import status

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

    def test_admin_cannot_access_student_only_profile_endpoint(self) -> None:
        response = self.admin_client.get("/api/students/me/profile/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
