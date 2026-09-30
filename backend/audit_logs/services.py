from __future__ import annotations

from audit_logs.models import AuditLog


def log_action(*, user, action: str, description: str) -> AuditLog:
    """Persist a simple audit event without changing schema."""

    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        description=description,
    )
