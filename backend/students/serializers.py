from rest_framework import serializers

from accounts.models import User
from students.models import Student


class StudentProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="user.role", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "student_code",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "is_active",
            "username",
            "role",
            "created_at",
            "updated_at",
        ]


class AdminStudentCreateSerializer(serializers.Serializer):
    student_code = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_student_code(self, value: str) -> str:
        normalized_value = value.strip()
        if Student.objects.filter(student_code=normalized_value).exists():
            raise serializers.ValidationError("دانشجویی با این کد قبلاً ثبت شده است.")
        if User.objects.filter(username=normalized_value).exists():
            raise serializers.ValidationError("کاربری با این کد دانشجویی قبلاً ثبت شده است.")
        return normalized_value

    def validate_phone_number(self, value: str) -> str:
        return value.strip()

    def validate_first_name(self, value: str) -> str:
        return value.strip()

    def validate_last_name(self, value: str) -> str:
        return value.strip()
