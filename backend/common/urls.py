from django.urls import path

from common.views import (
    AdminHomeView,
    AdminMealsView,
    AdminReportsView,
    AdminReservationsView,
    AdminSchedulesView,
    AdminSettingsPlaceholderView,
    AdminStudentsView,
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
    path("admin/", AdminHomeView.as_view(), name="web-admin-home"),
    path("admin/meals/", AdminMealsView.as_view(), name="web-admin-meals"),
    path("admin/schedules/", AdminSchedulesView.as_view(), name="web-admin-schedules"),
    path("admin/reservations/", AdminReservationsView.as_view(), name="web-admin-reservations"),
    path("admin/students/", AdminStudentsView.as_view(), name="web-admin-students"),
    path("admin/reports/", AdminReportsView.as_view(), name="web-admin-reports"),
    path("admin/settings/", AdminSettingsPlaceholderView.as_view(), name="web-admin-settings"),
    path("web/login/", StudentLoginPageView.as_view()),
    path("web/student/", StudentHomePlaceholderView.as_view()),
    path("web/student/schedule/", StudentScheduleView.as_view()),
    path("web/student/reservations/", StudentReservationListView.as_view()),
    path("web/student/profile/", StudentProfilePageView.as_view()),
    path("web/admin/", AdminHomeView.as_view()),
    path("web/admin/meals/", AdminMealsView.as_view()),
    path("web/admin/schedules/", AdminSchedulesView.as_view()),
    path("web/admin/reservations/", AdminReservationsView.as_view()),
    path("web/admin/students/", AdminStudentsView.as_view()),
    path("web/admin/reports/", AdminReportsView.as_view()),
    path("web/admin/settings/", AdminSettingsPlaceholderView.as_view()),
]
