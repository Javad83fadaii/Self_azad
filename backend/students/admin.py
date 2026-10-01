from django import forms
from django.contrib import admin
from django.db.models import Q

from accounts.models import UserRole
from .models import Student


class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user_field = self.fields.get("user")
        if user_field is None:
            return

        current_user_id = getattr(self.instance, "user_id", None)
        user_field.queryset = user_field.queryset.filter(
            role=UserRole.STUDENT,
        ).filter(
            Q(student_profile__isnull=True) | Q(pk=current_user_id)
        ).order_by("username")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ("student_code", "first_name", "last_name", "phone_number", "is_active")
    search_fields = ("student_code", "first_name", "last_name", "phone_number")
    list_filter = ("is_active",)
