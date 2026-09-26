from django.urls import path

from accounts.views import CsrfTokenView, CurrentUserView, LoginView, LogoutView, StudentRegistrationView, StudentWebLoginView

app_name = "accounts"

urlpatterns = [
    path("auth/csrf/", CsrfTokenView.as_view(), name="csrf"),
    path("auth/me/", CurrentUserView.as_view(), name="me"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/student/register/", StudentRegistrationView.as_view(), name="student-register"),
    path("auth/student/login/", StudentWebLoginView.as_view(), name="student-web-login"),
    path("auth/login/", LoginView.as_view(), name="login"),
]
