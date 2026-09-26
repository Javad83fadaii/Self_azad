from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole, IsStudentRole
from students.serializers import StudentProfileSerializer
from students.services import get_student_profile, list_students


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
