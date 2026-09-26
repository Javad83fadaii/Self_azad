from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from test_helpers import auth_client_for, create_meal, create_schedule, create_admin_account, create_student_account


class AuthenticationApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def _create_browser_client(self) -> APIClient:
        return APIClient(enforce_csrf_checks=True)

    def _issue_csrf_token(self, client: APIClient) -> str:
        response = client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.cookies["csrftoken"].value

    def _login_student_for_web(
        self,
        client: APIClient,
        *,
        student_code: str = "40110001",
        phone_number: str = "09120000000",
    ):
        csrf_token = self._issue_csrf_token(client)
        return client.post(
            "/api/auth/student/login/",
            {
                "student_code": student_code,
                "phone_number": phone_number,
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

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

    def test_student_web_login_creates_session(self) -> None:
        create_student_account(first_name="علی", last_name="احمدی")
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(browser_client)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["user"]["student_code"], "40110001")
        self.assertEqual(response.data["user"]["phone"], "09120000000")
        self.assertEqual(browser_client.session.get("_auth_user_id"), str(response.data["user"]["id"]))

    def test_student_web_login_rejects_invalid_credentials_with_generic_message(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(browser_client, phone_number="09121111111")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "اطلاعات ورود صحیح نیست.")

    def test_student_web_login_rejects_inactive_student(self) -> None:
        _, student = create_student_account()
        student.is_active = False
        student.save(update_fields=["is_active"])
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(browser_client)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "اطلاعات ورود صحیح نیست.")

    def test_student_web_login_rejects_inactive_user(self) -> None:
        user, _ = create_student_account()
        user.is_active = False
        user.save(update_fields=["is_active"])
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(browser_client)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "اطلاعات ورود صحیح نیست.")

    def test_current_user_returns_session_user_after_web_login(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()
        login_response = self._login_student_for_web(browser_client)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = browser_client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_code"], "40110001")
        self.assertEqual(response.data["phone"], "09120000000")
        self.assertEqual(response.data["role"], "STUDENT")

    def test_current_user_requires_authentication(self) -> None:
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalidates_current_session(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()
        login_response = self._login_student_for_web(browser_client)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        csrf_token = browser_client.cookies["csrftoken"].value

        logout_response = browser_client.post(
            "/api/auth/logout/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        me_response = browser_client.get("/api/auth/me/")

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertTrue(logout_response.data["success"])
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_desktop_token_login_is_preserved(self) -> None:
        create_student_account()

        response = self.client.post(
            "/api/auth/login/",
            {"username": "40110001", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["role"], "STUDENT")

    def test_desktop_token_auth_can_access_student_api(self) -> None:
        user, student = create_student_account()
        token_client = auth_client_for(user)

        response = token_client.get("/api/students/me/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_code"], student.student_code)

    def test_browser_post_requests_require_csrf_for_session_authentication(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()
        login_response = self._login_student_for_web(browser_client)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        meal = create_meal()
        schedule = create_schedule(meal=meal, capacity=2)

        response = browser_client.post(
            "/api/reservations/",
            {"meal_schedule_id": schedule.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
