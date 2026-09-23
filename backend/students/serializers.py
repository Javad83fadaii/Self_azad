from rest_framework import serializers

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
        ]
