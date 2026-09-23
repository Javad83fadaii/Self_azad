from __future__ import annotations

from rest_framework import serializers

from accounts.models import UserRole
from students.models import Student


class AuthUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    role = serializers.ChoiceField(choices=UserRole.choices, read_only=True)


class StudentRegistrationSerializer(serializers.Serializer):
    student_code = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class StudentRegistrationResponseSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "student_code",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "user",
        ]


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    user = AuthUserSerializer(read_only=True)
