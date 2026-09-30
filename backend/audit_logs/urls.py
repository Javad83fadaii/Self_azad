from django.urls import path

from audit_logs.views import AuditLogListView

app_name = "audit_logs"

urlpatterns = [
    path("admin/activity/", AuditLogListView.as_view(), name="admin-activity-list"),
]
