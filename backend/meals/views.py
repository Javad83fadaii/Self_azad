from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from audit_logs.services import log_action
from common.permissions import IsAdminRole, IsStudentRole
from meals.models import Meal, MealSchedule
from meals.serializers import MealScheduleSerializer, MealSerializer
from meals.services import (
    create_meal,
    create_schedule,
    deactivate_meal,
    deactivate_schedule,
    list_meals,
    list_schedules,
    list_upcoming_schedules,
    update_meal,
    update_schedule,
)


class MealListCreateView(APIView):
    """List meals for authenticated users or create a meal as admin."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        serializer = MealSerializer(list_meals(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = MealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meal = create_meal(**serializer.validated_data)
        log_action(
            user=request.user,
            action="ADMIN_MEAL_CREATE",
            description=f"ایجاد غذا: {meal.name} ({meal.code})",
        )
        return Response(MealSerializer(meal).data, status=status.HTTP_201_CREATED)


class ActiveMealListView(APIView):
    """List active meals for authenticated users."""

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        serializer = MealSerializer(list_meals(active_only=True), many=True)
        return Response(serializer.data)


class AdminMealListView(APIView):
    """List all meals for admin users."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = MealSerializer(list_meals(), many=True)
        return Response(serializer.data)


class MealDetailView(APIView):
    """Update or deactivate a meal as admin."""

    permission_classes = [IsAdminRole]

    def put(self, request, pk, *args, **kwargs):
        meal = get_object_or_404(Meal, pk=pk)
        serializer = MealSerializer(meal, data=request.data)
        serializer.is_valid(raise_exception=True)
        meal = update_meal(meal=meal, **serializer.validated_data)
        log_action(
            user=request.user,
            action="ADMIN_MEAL_UPDATE",
            description=f"ویرایش غذا: {meal.name} ({meal.code})",
        )
        return Response(MealSerializer(meal).data)

    def delete(self, request, pk, *args, **kwargs):
        meal = get_object_or_404(Meal, pk=pk)
        deactivate_meal(meal=meal)
        log_action(
            user=request.user,
            action="ADMIN_MEAL_DELETE",
            description=f"غیرفعال‌سازی غذا: {meal.name} ({meal.code})",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpcomingScheduleListView(APIView):
    """List active future schedules for students."""

    permission_classes = [IsStudentRole]

    def get(self, request, *args, **kwargs):
        serializer = MealScheduleSerializer(list_upcoming_schedules(), many=True)
        return Response(serializer.data)


class AdminScheduleListView(APIView):
    """List meal schedules for admin users."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = MealScheduleSerializer(list_schedules(), many=True)
        return Response(serializer.data)


class ScheduleListCreateView(APIView):
    """Create meal schedules as admin."""

    permission_classes = [IsAdminRole]

    def post(self, request, *args, **kwargs):
        serializer = MealScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = create_schedule(**serializer.validated_data)
        log_action(
            user=request.user,
            action="ADMIN_SCHEDULE_CREATE",
            description=f"ایجاد برنامه غذایی برای {schedule.meal.name} در تاریخ {schedule.date.isoformat()}",
        )
        return Response(MealScheduleSerializer(schedule).data, status=status.HTTP_201_CREATED)


class ScheduleDetailView(APIView):
    """Update or deactivate meal schedules as admin."""

    permission_classes = [IsAdminRole]

    def put(self, request, pk, *args, **kwargs):
        schedule = get_object_or_404(MealSchedule, pk=pk)
        serializer = MealScheduleSerializer(schedule, data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = update_schedule(schedule=schedule, **serializer.validated_data)
        log_action(
            user=request.user,
            action="ADMIN_SCHEDULE_UPDATE",
            description=f"ویرایش برنامه غذایی {schedule.id} برای {schedule.meal.name} در تاریخ {schedule.date.isoformat()}",
        )
        return Response(MealScheduleSerializer(schedule).data)

    def delete(self, request, pk, *args, **kwargs):
        schedule = get_object_or_404(MealSchedule, pk=pk)
        deactivate_schedule(schedule=schedule)
        log_action(
            user=request.user,
            action="ADMIN_SCHEDULE_DELETE",
            description=f"غیرفعال‌سازی برنامه غذایی {schedule.id} برای {schedule.meal.name} در تاریخ {schedule.date.isoformat()}",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
