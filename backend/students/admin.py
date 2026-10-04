from django import forms
from django.contrib import admin
from django.db import transaction
from django.db.models import Q

from accounts.models import User, UserRole
from .models import Student


class StudentAdminAddForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(render_value=False),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = Student
        fields = ("student_code", "first_name", "last_name", "phone_number", "is_active")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not password1 or not password2:
            raise forms.ValidationError("Both password fields are required.")

        if password1 != password2:
            raise forms.ValidationError("The two password fields did not match.")

        student_code = cleaned_data.get("student_code")
        if student_code and User.objects.filter(username=student_code).exists():
            self.add_error("student_code", "A user with this student code already exists.")

        return cleaned_data


class StudentAdminChangeForm(forms.ModelForm):
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

    def clean(self):
        cleaned_data = super().clean()
        student_code = cleaned_data.get("student_code")
        user = cleaned_data.get("user") or getattr(self.instance, "user", None)

        if student_code and user is not None:
            username_exists = User.objects.filter(username=student_code).exclude(pk=user.pk).exists()
            if username_exists:
                self.add_error("student_code", "A user with this student code already exists.")

        return cleaned_data


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminChangeForm
    add_form = StudentAdminAddForm
    list_display = ("student_code", "first_name", "last_name", "phone_number", "is_active")
    search_fields = ("student_code", "first_name", "last_name", "phone_number")
    list_filter = ("is_active",)

    def get_form(self, request, obj=None, **kwargs):
        kwargs["form"] = self.add_form if obj is None else self.form
        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("student_code", "first_name", "last_name", "phone_number", "is_active", "password1", "password2")
        return ("user", "student_code", "first_name", "last_name", "phone_number", "is_active")

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = User.objects.create_user(
                username=obj.student_code,
                password=form.cleaned_data["password1"],
                first_name=obj.first_name,
                last_name=obj.last_name,
                role=UserRole.STUDENT,
                is_active=obj.is_active,
            )
            super().save_model(request, obj, form, change)
            return

        obj.user.username = obj.student_code
        obj.user.first_name = obj.first_name
        obj.user.last_name = obj.last_name
        obj.user.is_active = obj.is_active
        obj.user.role = UserRole.STUDENT
        obj.user.save(update_fields=["username", "first_name", "last_name", "is_active", "role"])
        super().save_model(request, obj, form, change)
