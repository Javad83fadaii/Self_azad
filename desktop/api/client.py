from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(slots=True)
class ApiError(Exception):
    message: str
    status_code: int | None = None
    payload: Any = None

    def __str__(self) -> str:
        return self.message


class ApiClient:
    """Minimal synchronous REST client used by the desktop UI."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or os.getenv("API_BASE_URL") or "http://127.0.0.1:8000").rstrip("/") + "/"
        self.timeout = timeout
        self.token: str | None = None

    def set_token(self, token: str | None) -> None:
        self.token = token

    def resolve_url(self, path_or_url: str | None) -> str | None:
        if not path_or_url:
            return None
        return urljoin(self.base_url, path_or_url.lstrip("/"))

    def request(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> Any:
        headers = {"Accept": "application/json"}
        body: bytes | None = None

        if data is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
            body = json.dumps(data).encode("utf-8")

        if authenticated and self.token:
            headers["Authorization"] = f"Token {self.token}"

        request = Request(
            self.resolve_url(path) or path,
            data=body,
            headers=headers,
            method=method.upper(),
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw_body = response.read()
                if not raw_body:
                    return None
                return json.loads(raw_body.decode("utf-8"))
        except HTTPError as exc:
            payload = self._decode_error_payload(exc)
            raise ApiError(
                message=self._extract_error_message(payload) or f"HTTP {exc.code}",
                status_code=exc.code,
                payload=payload,
            ) from exc
        except URLError as exc:
            raise ApiError("اتصال به سرور برقرار نشد.") from exc
        except TimeoutError as exc:
            raise ApiError("پاسخ‌گویی سرور بیش از حد طول کشید.") from exc

    def fetch_binary(self, path_or_url: str) -> bytes:
        request = Request(self.resolve_url(path_or_url) or path_or_url, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise ApiError("دریافت تصویر با مشکل روبه‌رو شد.") from exc

    @staticmethod
    def _decode_error_payload(exc: HTTPError) -> Any:
        try:
            raw_body = exc.read()
        except Exception:
            raw_body = b""

        if not raw_body:
            return None

        try:
            return json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return raw_body.decode("utf-8", errors="ignore")

    @staticmethod
    def _extract_error_message(payload: Any) -> str | None:
        if payload is None:
            return None
        if isinstance(payload, str):
            return payload
        if isinstance(payload, list):
            return ", ".join(str(item) for item in payload if item is not None) or None
        if isinstance(payload, dict):
            if payload.get("detail"):
                return str(payload["detail"])
            messages: list[str] = []
            for value in payload.values():
                if isinstance(value, list):
                    messages.extend(str(item) for item in value)
                else:
                    messages.append(str(value))
            return "، ".join(message for message in messages if message) or None
        return str(payload)
