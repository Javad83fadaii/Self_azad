from django.urls import path

from reservations.views import (
    MyReservationListView,
    ReservationByDateListView,
    ReservationByMealListView,
    ReservationCancelView,
    ReservationCreateView,
    ReservationListView,
)

app_name = "reservations"

urlpatterns = [
    path("reservations/", ReservationCreateView.as_view(), name="reservation-create"),
    path("reservations/my/", MyReservationListView.as_view(), name="reservation-my-list"),
    path("reservations/<int:pk>/cancel/", ReservationCancelView.as_view(), name="reservation-cancel"),
    path("admin/reservations/", ReservationListView.as_view(), name="reservation-admin-list"),
    path("admin/reservations/by-date/", ReservationByDateListView.as_view(), name="reservation-by-date"),
    path("admin/reservations/by-meal/", ReservationByMealListView.as_view(), name="reservation-by-meal"),
]
