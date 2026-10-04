from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from audit_logs.services import log_action
from common.permissions import IsAdminRole, IsStudentRole
from students.serializers import AdminStudentCreateSerializer, StudentProfileSerializer
from students.services import create_student, get_student_profile, list_students


class StudentProfileView(APIView):
    """Return the authenticated student's profile."""

    permission_classes = [IsStudentRole]

    def get(self, request, *args, **kwargs):
        student = get_student_profile(user=request.user)
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)


class AdminStudentListView(APIView):
    """List student records for admin users."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = StudentProfileSerializer(list_students(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = AdminStudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = create_student(**serializer.validated_data)
        log_action(
            user=request.user,
            action="ADMIN_STUDENT_CREATE",
            description=f"ایجاد دانشجو: {student.full_name} ({student.student_code})",
        )
        return Response(StudentProfileSerializer(student).data, status=status.HTTP_201_CREATED)
