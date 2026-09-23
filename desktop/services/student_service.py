from __future__ import annotations

from typing import Any

from desktop.api.client import ApiClient


class StudentApiService:
    """Service layer for student desktop screens."""

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def login(self, *, username: str, password: str) -> dict[str, Any]:
        return self.api_client.request(
            "POST",
            "/api/auth/login/",
            data={"username": username, "password": password},
            authenticated=False,
        )

    def get_profile(self) -> dict[str, Any]:
        return self.api_client.request("GET", "/api/students/me/profile/")

    def get_upcoming_schedules(self) -> list[dict[str, Any]]:
        return self.api_client.request("GET", "/api/schedules/upcoming/")

    def get_my_reservations(self) -> list[dict[str, Any]]:
        return self.api_client.request("GET", "/api/reservations/my/")

    def create_reservation(self, *, meal_schedule_id: int) -> dict[str, Any]:
        return self.api_client.request(
            "POST",
            "/api/reservations/",
            data={"meal_schedule_id": meal_schedule_id},
        )

    def cancel_reservation(self, *, reservation_id: int) -> dict[str, Any]:
        return self.api_client.request("DELETE", f"/api/reservations/{reservation_id}/cancel/")
