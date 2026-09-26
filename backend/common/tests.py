from __future__ import annotations

import json

from django.test import Client, TestCase

from test_helpers import create_admin_account, create_student_account


class WebUiShellTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def _create_browser_client(self) -> Client:
        return Client(enforce_csrf_checks=True)

    def _issue_csrf_token(self, client: Client) -> str:
        response = client.get("/login/")
        self.assertEqual(response.status_code, 200)
        return response.cookies["csrftoken"].value

    def _login_student_for_web(
        self,
        client: Client,
        *,
        student_code: str = "40110001",
        phone_number: str = "09120000000",
    ):
        csrf_token = self._issue_csrf_token(client)
        return client.post(
            "/api/auth/student/login/",
            data=json.dumps(
                {
                    "student_code": student_code,
                    "phone_number": phone_number,
                }
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def test_login_page_is_available(self) -> None:
        response = self.client.get("/login/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "سامانه رزرو غذای دانشگاه")
        self.assertContains(response, "ورود دانشجو")
        self.assertContains(response, "ورود به سامانه")

    def test_student_dashboard_redirects_to_login_when_unauthenticated(self) -> None:
        response = self.client.get("/student/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/student/")

    def test_admin_dashboard_redirects_to_login_when_unauthenticated(self) -> None:
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/admin/")

    def test_student_can_login_and_open_student_dashboard(self) -> None:
        create_student_account(first_name="علی", last_name="احمدی")
        browser_client = self._create_browser_client()

        login_response = self._login_student_for_web(browser_client)
        dashboard_response = browser_client.get("/student/")

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, "سلام، علی احمدی")
        self.assertContains(dashboard_response, "فضای دانشجو")

    def test_admin_dashboard_is_available_for_logged_in_admin(self) -> None:
        admin_user = create_admin_account()
        self.client.force_login(admin_user)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد مدیریت")
        self.assertContains(response, "پنل مدیریت")

    def test_student_cannot_access_admin_dashboard(self) -> None:
        student_user, _ = create_student_account()
        self.client.force_login(student_user)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_access_student_dashboard(self) -> None:
        admin_user = create_admin_account()
        self.client.force_login(admin_user)

        response = self.client.get("/student/")

        self.assertEqual(response.status_code, 403)

    def test_logout_clears_session_and_student_dashboard_requires_login_again(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()
        login_response = self._login_student_for_web(browser_client)
        self.assertEqual(login_response.status_code, 200)

        csrf_token = browser_client.cookies["csrftoken"].value
        logout_response = browser_client.post(
            "/api/auth/logout/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        dashboard_response = browser_client.get("/student/")

        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(dashboard_response.status_code, 302)
        self.assertEqual(dashboard_response.url, "/login/?next=/student/")
