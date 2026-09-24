from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts.serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    StudentRegistrationResponseSerializer,
    StudentRegistrationSerializer,
)
from accounts.services import login_user, register_student


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
