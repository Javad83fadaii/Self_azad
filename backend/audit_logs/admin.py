from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "created_at")
    search_fields = ("action", "description", "user__username")
    list_filter = ("action", "created_at")
