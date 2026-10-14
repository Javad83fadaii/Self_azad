from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from students.models import Student
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
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        csrf_token = self._issue_csrf_token(client)
        payload = {
            "student_code": student_code,
            "phone_number": phone_number,
        }
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        return client.post(
            "/api/auth/student/login/",
            payload,
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def _login_admin_for_web(
        self,
        client: APIClient,
        *,
        username: str = "admin",
        password: str = "AdminPass123",
    ):
        csrf_token = self._issue_csrf_token(client)
        return client.post(
            "/api/auth/admin/login/",
            {
                "username": username,
                "password": password,
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

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

    def test_student_web_login_requests_profile_completion_for_first_login(self) -> None:
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(
            browser_client,
            student_code="40119999",
            phone_number="09123334444",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "برای اولین ورود، نام و نام خانوادگی را هم وارد کنید.")
        self.assertTrue(response.data["requires_profile_completion"])

    def test_student_web_login_creates_student_account_on_first_login_when_names_are_provided(self) -> None:
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(
            browser_client,
            student_code="۴۰۱۱۹۹۹۹",
            phone_number="۰۹۱۲۳۳۳۴۴۴۴",
            first_name="سارا",
            last_name="کریمی",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["user"]["student_code"], "40119999")
        self.assertEqual(response.data["user"]["phone"], "09123334444")
        self.assertEqual(browser_client.session.get("_auth_user_id"), str(response.data["user"]["id"]))

        student = Student.objects.select_related("user").get(student_code="40119999")
        self.assertEqual(student.first_name, "سارا")
        self.assertEqual(student.last_name, "کریمی")
        self.assertEqual(student.phone_number, "09123334444")
        self.assertEqual(student.user.first_name, "سارا")
        self.assertEqual(student.user.last_name, "کریمی")
        self.assertFalse(student.user.has_usable_password())

    def test_student_web_login_completes_incomplete_profile_when_names_are_provided(self) -> None:
        user, student = create_student_account(first_name="", last_name="")
        student.phone_number = "09125556666"
        student.save(update_fields=["phone_number"])
        user.first_name = ""
        user.last_name = ""
        user.save(update_fields=["first_name", "last_name"])
        browser_client = self._create_browser_client()

        initial_response = self._login_student_for_web(
            browser_client,
            phone_number="09125556666",
        )

        self.assertEqual(initial_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(initial_response.data["requires_profile_completion"])

        response = self._login_student_for_web(
            browser_client,
            phone_number="09125556666",
            first_name="علی",
            last_name="احمدی",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        student.refresh_from_db()
        user.refresh_from_db()
        self.assertEqual(student.first_name, "علی")
        self.assertEqual(student.last_name, "احمدی")
        self.assertEqual(user.first_name, "علی")
        self.assertEqual(user.last_name, "احمدی")

    def test_student_web_login_requires_student_code_and_phone_number_payload(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()
        csrf_token = self._issue_csrf_token(browser_client)

        response = browser_client.post(
            "/api/auth/student/login/",
            {
                "username": "40110001",
                "password": "StrongPass123",
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("student_code", response.data)
        self.assertIn("phone_number", response.data)

    def test_student_web_login_accepts_normalized_phone_number(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(browser_client, phone_number="+98 912 000 0000")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

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

    def test_student_web_login_rejects_student_profile_linked_to_admin_user(self) -> None:
        admin_user = create_admin_account(username="javad")

        Student.objects.create(
            user=admin_user,
            student_code="40215441054217",
            first_name="Test",
            last_name="Student",
            phone_number="09104648477",
            is_active=True,
        )
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(
            browser_client,
            student_code="40215441054217",
            phone_number="09104648477",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "اطلاعات ورود صحیح نیست.")

    def test_student_web_login_rejects_orphan_username_conflict_on_first_login(self) -> None:
        User.objects.create_user(
            username="40118888",
            password=None,
            first_name="Test",
            last_name="User",
        )
        browser_client = self._create_browser_client()

        response = self._login_student_for_web(
            browser_client,
            student_code="40118888",
            phone_number="09127778888",
            first_name="رضا",
            last_name="کریمی",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "اطلاعات ورود صحیح نیست.")

    def test_admin_web_login_creates_session(self) -> None:
        create_admin_account()
        browser_client = self._create_browser_client()

        response = self._login_admin_for_web(browser_client)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["user"]["role"], "ADMIN")
        self.assertEqual(response.data["user"]["username"], "admin")
        self.assertEqual(browser_client.session.get("_auth_user_id"), str(response.data["user"]["id"]))

    def test_admin_web_login_rejects_invalid_credentials_with_generic_message(self) -> None:
        create_admin_account()
        browser_client = self._create_browser_client()

        response = self._login_admin_for_web(browser_client, password="WrongPass123")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "اطلاعات ورود صحیح نیست.")

    def test_admin_web_login_rejects_student_role_account(self) -> None:
        create_student_account()
        browser_client = self._create_browser_client()

        response = self._login_admin_for_web(
            browser_client,
            username="40110001",
            password="StrongPass123",
        )

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

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        self.assertEqual(me_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_access_student_api(self) -> None:
        user, student = create_student_account()
        authenticated_client = auth_client_for(user)

        response = authenticated_client.get("/api/students/me/profile/")

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
