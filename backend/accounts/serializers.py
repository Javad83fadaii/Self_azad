from __future__ import annotations

from rest_framework import serializers

from accounts.models import UserRole


class StudentWebLoginSerializer(serializers.Serializer):
    student_code = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_student_code(self, value: str) -> str:
        return value.strip()

    def validate_phone_number(self, value: str) -> str:
        return value.strip()

    def validate_first_name(self, value: str) -> str:
        return value.strip()

    def validate_last_name(self, value: str) -> str:
        return value.strip()


class AdminWebLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    student_id = serializers.IntegerField(read_only=True, required=False, allow_null=True)
    student_code = serializers.CharField(read_only=True, required=False, allow_null=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True, required=False, allow_null=True)
    role = serializers.ChoiceField(choices=UserRole.choices, read_only=True)
    is_active = serializers.BooleanField(read_only=True)


class WebLoginResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(read_only=True)
    user = CurrentUserSerializer(read_only=True)
