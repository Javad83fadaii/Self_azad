from django.urls import path

from meals.views import (
    ActiveMealListView,
    MealDetailView,
    MealListCreateView,
    ScheduleDetailView,
    ScheduleListCreateView,
    UpcomingScheduleListView,
)

app_name = "meals"

urlpatterns = [
    path("meals/", MealListCreateView.as_view(), name="meal-list-create"),
    path("meals/active/", ActiveMealListView.as_view(), name="meal-active-list"),
    path("meals/<int:pk>/", MealDetailView.as_view(), name="meal-detail"),
    path("schedules/upcoming/", UpcomingScheduleListView.as_view(), name="schedule-upcoming"),
    path("schedules/", ScheduleListCreateView.as_view(), name="schedule-list-create"),
    path("schedules/<int:pk>/", ScheduleDetailView.as_view(), name="schedule-detail"),
]
