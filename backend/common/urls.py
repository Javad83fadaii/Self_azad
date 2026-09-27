from django.urls import path

from common.views import (
    AdminHomePlaceholderView,
    StudentHomePlaceholderView,
    StudentLoginPageView,
    StudentProfilePageView,
    StudentReservationListView,
    StudentScheduleView,
    WebEntryRedirectView,
)

app_name = "common"

urlpatterns = [
    path("", WebEntryRedirectView.as_view(), name="web-entry"),
    path("login/", StudentLoginPageView.as_view(), name="web-login"),
    path("student/", StudentHomePlaceholderView.as_view(), name="web-student-home"),
    path("student/schedule/", StudentScheduleView.as_view(), name="web-student-schedule"),
    path("student/reservations/", StudentReservationListView.as_view(), name="web-student-reservations"),
    path("student/profile/", StudentProfilePageView.as_view(), name="web-student-profile"),
    path("admin/", AdminHomePlaceholderView.as_view(), name="web-admin-home"),
    path("web/login/", StudentLoginPageView.as_view()),
    path("web/student/", StudentHomePlaceholderView.as_view()),
    path("web/student/schedule/", StudentScheduleView.as_view()),
    path("web/student/reservations/", StudentReservationListView.as_view()),
    path("web/student/profile/", StudentProfilePageView.as_view()),
    path("web/admin/", AdminHomePlaceholderView.as_view()),
]
