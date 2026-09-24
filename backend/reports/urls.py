from django.urls import path

from reports.views import DailyMealReportView, MealReportView, StudentReportView

urlpatterns = [
    path("admin/reports/daily-meals/", DailyMealReportView.as_view(), name="admin-daily-meal-report"),
    path("admin/reports/students/", StudentReportView.as_view(), name="admin-student-report"),
    path("admin/reports/meals/", MealReportView.as_view(), name="admin-meal-report"),
]
