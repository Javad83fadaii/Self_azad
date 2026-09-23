from accounts.models import UserRole
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == UserRole.ADMIN)


class IsStudentRole(BasePermission):
    """Allow access only to student users with an attached profile."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == UserRole.STUDENT
            and hasattr(user, "student_profile")
        )
