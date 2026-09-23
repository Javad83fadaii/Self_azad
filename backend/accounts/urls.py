from django.urls import path

from accounts.views import LoginView, StudentRegistrationView

app_name = "accounts"

urlpatterns = [
    path("auth/student/register/", StudentRegistrationView.as_view(), name="student-register"),
    path("auth/login/", LoginView.as_view(), name="login"),
]
