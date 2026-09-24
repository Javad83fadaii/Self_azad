from django.urls import path

from dashboard.views import DashboardAnalyticsView

urlpatterns = [
    path("admin/dashboard/", DashboardAnalyticsView.as_view(), name="admin-dashboard"),
]
