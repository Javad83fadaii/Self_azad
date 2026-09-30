from rest_framework.response import Response
from rest_framework.views import APIView

from audit_logs.services import log_action
from common.permissions import IsAdminRole
from reports.serializers import (
    DailyMealReportFilterSerializer,
    DailyMealReportResponseSerializer,
    MealReportFilterSerializer,
    MealReportResponseSerializer,
    ReservationReportFilterSerializer,
    ReservationReportResponseSerializer,
    StudentReportFilterSerializer,
    StudentReportResponseSerializer,
)
from reports.services import (
    export_report,
    get_daily_meal_report,
    get_meal_report,
    get_reservation_report,
    get_student_report,
)


class DailyMealReportView(APIView):
    """Return meal report rows for a selected date."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = DailyMealReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        export_format = serializer.validated_data.pop("export", None)
        report_range = serializer.validated_data
        results = get_daily_meal_report(**report_range)
        start_date = report_range["start_date"]
        end_date = report_range["end_date"]
        single_date = report_range.get("date") or (start_date if start_date == end_date else None)

        if export_format:
            log_action(
                user=request.user,
                action="ADMIN_REPORT_EXPORT",
                description=f"خروجی {export_format.upper()} گزارش روزانه غذاها برای بازه {start_date} تا {end_date}",
            )
            return export_report(
                filename=f"daily_meal_report_{start_date.isoformat()}_{end_date.isoformat()}",
                title="گزارش روزانه غذاها",
                sheet_name="DailyMealReport",
                headers=[
                    "شناسه برنامه",
                    "تاریخ",
                    "شناسه غذا",
                    "نام غذا",
                    "تعداد رزرو",
                    "لغوشده",
                    "ظرفیت",
                    "ظرفیت باقی‌مانده",
                    "درصد استفاده",
                ],
                rows=[
                    [
                        item["schedule_id"],
                        item["date"],
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
                start_date=start_date,
                end_date=end_date,
            )

        response_serializer = DailyMealReportResponseSerializer(
            data={
                "date": single_date,
                "start_date": start_date,
                "end_date": end_date,
                "count": len(results),
                "results": results,
            }
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
        report_data = get_student_report(**serializer.validated_data)

        if export_format:
            log_action(
                user=request.user,
                action="ADMIN_REPORT_EXPORT",
                description=f"خروجی {export_format.upper()} گزارش دانشجویان",
            )
            return export_report(
                filename="student_report",
                title="گزارش دانشجویان",
                sheet_name="StudentReport",
                headers=[
                    "شناسه دانشجو",
                    "کد دانشجویی",
                    "نام",
                    "نام خانوادگی",
                    "نام کامل",
                    "شماره موبایل",
                    "وضعیت فعال",
                    "کل رزروها",
                    "لغوشده",
                    "مصرف‌شده",
                    "عدم مراجعه",
                    "رزرو فعال",
                ],
                rows=[
                    [
                        item["student_id"],
                        item["student_code"],
                        item["first_name"],
                        item["last_name"],
                        item["full_name"],
                        item["phone_number"],
                        "فعال" if item["is_active"] else "غیرفعال",
                        item["total_reservations"],
                        item["cancelled_count"],
                        item["used_count"],
                        item["no_show_count"],
                        item["active_reservations"],
                    ]
                    for item in report_data["results"]
                ],
                export_format=export_format,
                start_date=report_data["start_date"],
                end_date=report_data["end_date"],
            )

        response_serializer = StudentReportResponseSerializer(
            data={
                "start_date": report_data["start_date"],
                "end_date": report_data["end_date"],
                "count": len(report_data["results"]),
                "summary": report_data["summary"],
                "results": report_data["results"],
            }
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
        report_data = get_meal_report(
            start_date=serializer.validated_data.get("start_date"),
            end_date=serializer.validated_data.get("end_date"),
        )

        if export_format:
            log_action(
                user=request.user,
                action="ADMIN_REPORT_EXPORT",
                description=f"خروجی {export_format.upper()} گزارش عملکرد غذاها",
            )
            return export_report(
                filename="meal_report",
                title="گزارش عملکرد غذاها",
                sheet_name="MealReport",
                headers=[
                    "شناسه غذا",
                    "نام غذا",
                    "کد غذا",
                    "تعداد دفعات ارائه",
                    "مجموع رزرو",
                    "میانگین رزرو",
                    "بیشترین رزرو",
                    "کمترین رزرو",
                    "لغوشده",
                    "مصرف‌شده",
                    "عدم مراجعه",
                    "ظرفیت",
                    "درصد استفاده",
                ],
                rows=[
                    [
                        item["meal_id"],
                        item["meal_name"],
                        item["meal_code"],
                        item["service_count"],
                        item["total_reservations"],
                        item["average_reservations"],
                        item["max_reservations"],
                        item["min_reservations"],
                        item["cancelled_count"],
                        item["used_count"],
                        item["no_show_count"],
                        item["capacity"],
                        item["utilization_percentage"],
                    ]
                    for item in report_data["results"]
                ],
                export_format=export_format,
                start_date=report_data["start_date"],
                end_date=report_data["end_date"],
            )

        response_serializer = MealReportResponseSerializer(
            data={
                "start_date": report_data["start_date"],
                "end_date": report_data["end_date"],
                "count": len(report_data["results"]),
                "summary": report_data["summary"],
                "results": report_data["results"],
            }
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)


class ReservationReportView(APIView):
    """Return reservation statistics and trend rows."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = ReservationReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        report_data = get_reservation_report(
            start_date=serializer.validated_data.get("start_date"),
            end_date=serializer.validated_data.get("end_date"),
        )
        response_serializer = ReservationReportResponseSerializer(data=report_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)
