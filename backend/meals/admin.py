from django.contrib import admin

from .models import Meal, MealSchedule


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "price", "is_active", "created_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(MealSchedule)
class MealScheduleAdmin(admin.ModelAdmin):
    list_display = ("meal", "date", "capacity", "is_active")
    search_fields = ("meal__name", "meal__code")
    list_filter = ("is_active", "date")
