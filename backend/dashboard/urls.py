from django.urls import path

from dashboard.views import DashboardAnalyticsView

app_name = "dashboard"

urlpatterns = [
    path("admin/dashboard/", DashboardAnalyticsView.as_view(), name="admin-dashboard"),
]
