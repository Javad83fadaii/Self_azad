from django.urls import path

from common.views import (
    AdminHomePlaceholderView,
    StudentHomePlaceholderView,
    StudentLoginPageView,
    WebEntryRedirectView,
)

app_name = "common"

urlpatterns = [
    path("", WebEntryRedirectView.as_view(), name="web-entry"),
    path("login/", StudentLoginPageView.as_view(), name="web-login"),
    path("student/", StudentHomePlaceholderView.as_view(), name="web-student-home"),
    path("admin/", AdminHomePlaceholderView.as_view(), name="web-admin-home"),
    path("web/login/", StudentLoginPageView.as_view()),
    path("web/student/", StudentHomePlaceholderView.as_view()),
    path("web/admin/", AdminHomePlaceholderView.as_view()),
]
