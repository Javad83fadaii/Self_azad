from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "reservation_code",
        "student",
        "meal_schedule",
        "reservation_date",
        "status",
        "created_at",
    )
    search_fields = ("reservation_code", "student__student_code")
    list_filter = ("status", "reservation_date")
