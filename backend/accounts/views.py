from __future__ import annotations

from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts.serializers import (
    CurrentUserSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    StudentWebLoginResponseSerializer,
    StudentWebLoginSerializer,
    StudentRegistrationResponseSerializer,
    StudentRegistrationSerializer,
)
from accounts.services import build_current_user_payload, login_student_for_web, login_user, register_student


class StudentRegistrationView(APIView):
    """Register a student account and create its linked student profile."""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = StudentRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = register_student(**serializer.validated_data)
        response_serializer = StudentRegistrationResponseSerializer(student)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a user and return a DRF token."""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, user = login_user(**serializer.validated_data)
        response_serializer = LoginResponseSerializer(
            {
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(APIView):
    """Issue a CSRF cookie for browser-based clients."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "success": True,
                "csrfToken": get_token(request),
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_protect, name="dispatch")
class StudentWebLoginView(APIView):
    """Authenticate a student for browser usage via Django sessions."""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = StudentWebLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = login_student_for_web(**serializer.validated_data)
        django_login(request, student.user, backend="django.contrib.auth.backends.ModelBackend")
        response_serializer = StudentWebLoginResponseSerializer(
            {
                "success": True,
                "user": build_current_user_payload(user=student.user),
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Invalidate the current authenticated session."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        django_logout(request)
        return Response({"success": True}, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """Return the currently authenticated user for session or token clients."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = CurrentUserSerializer(build_current_user_payload(user=request.user))
        return Response(serializer.data, status=status.HTTP_200_OK)
