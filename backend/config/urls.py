"""Root URL configuration for the UFRS backend."""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("common.urls")),
    path("api/schema/", get_schema_view(title="UFRS API", version="3.0.0"), name="api-schema"),
    path("api/", include("accounts.urls")),
    path("api/", include("students.urls")),
    path("api/", include("meals.urls")),
    path("api/", include("reservations.urls")),
    path("api/", include("dashboard.urls")),
    path("api/", include("reports.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
