from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole
from reports.serializers import (
    DailyMealReportFilterSerializer,
    DailyMealReportResponseSerializer,
    MealReportFilterSerializer,
    MealReportResponseSerializer,
    StudentReportFilterSerializer,
    StudentReportResponseSerializer,
)
from reports.services import export_report, get_daily_meal_report, get_meal_report, get_student_report


class DailyMealReportView(APIView):
    """Return meal report rows for a selected date."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = DailyMealReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        export_format = serializer.validated_data.pop("export", None)
        report_date = serializer.validated_data["date"]
        results = get_daily_meal_report(date=report_date)

        if export_format:
            return export_report(
                filename=f"daily_meal_report_{report_date.isoformat()}",
                title=f"Daily Meal Report - {report_date.isoformat()}",
                sheet_name="DailyMealReport",
                headers=[
                    "Schedule ID",
                    "Meal ID",
                    "Meal Name",
                    "Reservations",
                    "Cancelled",
                    "Capacity",
                    "Remaining Capacity",
                    "Utilization %",
                ],
                rows=[
                    [
                        item["schedule_id"],
                        item["meal_id"],
                        item["meal_name"],
                        item["reservation_count"],
                        item["cancelled_count"],
                        item["capacity"],
                        item["remaining_capacity"],
                        item["utilization_percentage"],
                    ]
                    for item in results
                ],
                export_format=export_format,
            )

        response_serializer = DailyMealReportResponseSerializer(
            data={"date": report_date, "results": results}
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)


class StudentReportView(APIView):
    """Return student report rows with field-based search."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = StudentReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        export_format = serializer.validated_data.pop("export", None)
        results = get_student_report(**serializer.validated_data)

        if export_format:
            return export_report(
                filename="student_report",
                title="Student Report",
                sheet_name="StudentReport",
                headers=[
                    "Student ID",
                    "Student Code",
                    "First Name",
                    "Last Name",
                    "Full Name",
                    "Phone Number",
                    "Total Reservations",
                    "Cancelled",
                    "Used",
                    "No Show",
                    "Active Reservations",
                ],
                rows=[
                    [
                        item["student_id"],
                        item["student_code"],
                        item["first_name"],
                        item["last_name"],
                        item["full_name"],
                        item["phone_number"],
                        item["total_reservations"],
                        item["cancelled_count"],
                        item["used_count"],
                        item["no_show_count"],
                        item["active_reservations"],
                    ]
                    for item in results
                ],
                export_format=export_format,
            )

        response_serializer = StudentReportResponseSerializer(
            data={"count": len(results), "results": results}
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)


class MealReportView(APIView):
    """Return aggregated meal report rows."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = MealReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        export_format = serializer.validated_data.get("export")
        results = get_meal_report()

        if export_format:
            return export_report(
                filename="meal_report",
                title="Meal Report",
                sheet_name="MealReport",
                headers=[
                    "Meal ID",
                    "Meal Name",
                    "Meal Code",
                    "Total Reservations",
                    "Cancelled",
                    "Used",
                    "No Show",
                    "Capacity",
                    "Utilization %",
                ],
                rows=[
                    [
                        item["meal_id"],
                        item["meal_name"],
                        item["meal_code"],
                        item["total_reservations"],
                        item["cancelled_count"],
                        item["used_count"],
                        item["no_show_count"],
                        item["capacity"],
                        item["utilization_percentage"],
                    ]
                    for item in results
                ],
                export_format=export_format,
            )

        response_serializer = MealReportResponseSerializer(data={"count": len(results), "results": results})
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)
