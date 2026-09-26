from django.urls import path

from students.views import AdminStudentListView, StudentProfileView

app_name = "students"

urlpatterns = [
    path("admin/students/", AdminStudentListView.as_view(), name="admin-student-list"),
    path("students/me/profile/", StudentProfileView.as_view(), name="student-profile"),
]
