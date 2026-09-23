from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsStudentRole
from students.serializers import StudentProfileSerializer
from students.services import get_student_profile


class StudentProfileView(APIView):
    """Return the authenticated student's profile."""

    permission_classes = [IsStudentRole]

    def get(self, request, *args, **kwargs):
        student = get_student_profile(user=request.user)
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)
