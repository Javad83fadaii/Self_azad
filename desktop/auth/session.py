from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuthSession:
    """In-memory authentication state for the student desktop client."""

    token: str | None = None
    user: dict[str, Any] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token)

    def start(self, *, token: str, user: dict[str, Any]) -> None:
        self.token = token
        self.user = dict(user)

    def clear(self) -> None:
        self.token = None
        self.user.clear()
