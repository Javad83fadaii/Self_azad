from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_code", "first_name", "last_name", "phone_number", "is_active")
    search_fields = ("student_code", "first_name", "last_name", "phone_number")
    list_filter = ("is_active",)
