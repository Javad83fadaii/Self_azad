from django.test import TestCase
from rest_framework import status

from audit_logs.services import log_action
from test_helpers import auth_client_for, create_admin_account, create_student_account


class AuditLogApiTests(TestCase):
    def setUp(self) -> None:
        self.admin_user = create_admin_account()
        self.student_user, _ = create_student_account()
        self.admin_client = auth_client_for(self.admin_user)
        self.student_client = auth_client_for(self.student_user)

        log_action(
            user=self.admin_user,
            action="ADMIN_REPORT_EXPORT",
            description="خروجی گزارش عملکرد غذاها",
        )
        log_action(
            user=self.admin_user,
            action="ADMIN_PAGE_VIEW",
            description="نمایش صفحه گزارش‌ها",
        )

    def test_admin_can_list_audit_logs(self) -> None:
        response = self.admin_client.get("/api/admin/activity/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["action"], "ADMIN_PAGE_VIEW")
        self.assertEqual(response.data["results"][1]["action"], "ADMIN_REPORT_EXPORT")

    def test_admin_can_filter_audit_logs(self) -> None:
        response = self.admin_client.get(
            "/api/admin/activity/",
            {"action": "EXPORT", "username": self.admin_user.username},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "ADMIN_REPORT_EXPORT")

    def test_student_cannot_access_audit_logs(self) -> None:
        response = self.student_client.get("/api/admin/activity/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
