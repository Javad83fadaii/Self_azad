from django.urls import path

from students.views import StudentProfileView

app_name = "students"

urlpatterns = [
    path("students/me/profile/", StudentProfileView.as_view(), name="student-profile"),
]
