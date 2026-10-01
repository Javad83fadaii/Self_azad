from __future__ import annotations

import csv
from collections import defaultdict
from io import BytesIO, StringIO

from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from meals.models import Meal, MealSchedule
from reservations.models import Reservation, ReservationStatus
from students.models import Student

OCCUPIED_STATUSES = [
    ReservationStatus.RESERVED,
    ReservationStatus.USED,
    ReservationStatus.NO_SHOW,
]


def _calculate_utilization(*, reserved_count: int, capacity: int) -> float:
    if capacity <= 0:
        return 0.0
    return round((reserved_count / capacity) * 100, 2)


def _resolve_report_range(*, date=None, start_date=None, end_date=None):
    if date is not None:
        return date, date
    if start_date and end_date:
        return start_date, end_date
    if start_date:
        return start_date, start_date
    if end_date:
        return end_date, end_date
    return None, None


def _format_report_range(*, start_date=None, end_date=None) -> str:
    if start_date and end_date:
        if start_date == end_date:
            return start_date.isoformat()
        return f"{start_date.isoformat()} تا {end_date.isoformat()}"
    return "همه داده‌های موجود"


def get_daily_meal_report(*, date=None, start_date=None, end_date=None):
    start_date, end_date = _resolve_report_range(
        date=date,
        start_date=start_date,
        end_date=end_date,
    )
    schedules = (
        MealSchedule.objects.select_related("meal")
        .filter(date__range=(start_date, end_date))
        .annotate(
            reservation_count=Count(
                "reservations",
                filter=Q(reservations__status__in=OCCUPIED_STATUSES),
            ),
            cancelled_count=Count(
                "reservations",
                filter=Q(reservations__status=ReservationStatus.CANCELLED),
            ),
        )
        .order_by("meal__name")
    )

    results = []
    for schedule in schedules:
        results.append(
            {
                "schedule_id": schedule.id,
                "date": schedule.date,
                "meal_id": schedule.meal_id,
                "meal_name": schedule.meal.name,
                "reservation_count": schedule.reservation_count,
                "cancelled_count": schedule.cancelled_count,
                "capacity": schedule.capacity,
                "remaining_capacity": max(schedule.capacity - schedule.reservation_count, 0),
                "utilization_percentage": _calculate_utilization(
                    reserved_count=schedule.reservation_count,
                    capacity=schedule.capacity,
                ),
            }
        )
    return results


def get_student_report(
    *,
    start_date=None,
    end_date=None,
    student_code: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    phone_number: str | None = None,
):
    start_date, end_date = _resolve_report_range(start_date=start_date, end_date=end_date)
    reservation_filter = Q()
    if start_date and end_date:
        reservation_filter &= Q(reservations__meal_schedule__date__range=(start_date, end_date))

    queryset = Student.objects.select_related("user").annotate(
        total_reservations=Count("reservations", filter=reservation_filter),
        cancelled_count=Count(
            "reservations",
            filter=reservation_filter & Q(reservations__status=ReservationStatus.CANCELLED),
        ),
        used_count=Count(
            "reservations",
            filter=reservation_filter & Q(reservations__status=ReservationStatus.USED),
        ),
        no_show_count=Count(
            "reservations",
            filter=reservation_filter & Q(reservations__status=ReservationStatus.NO_SHOW),
        ),
        active_reservations=Count(
            "reservations",
            filter=reservation_filter & Q(reservations__status=ReservationStatus.RESERVED),
        ),
    )

    if student_code:
        queryset = queryset.filter(student_code__icontains=student_code)
    if first_name:
        queryset = queryset.filter(first_name__icontains=first_name)
    if last_name:
        queryset = queryset.filter(last_name__icontains=last_name)
    if phone_number:
        queryset = queryset.filter(phone_number__icontains=phone_number)

    results = []
    for student in queryset.order_by("student_code"):
        results.append(
            {
                "student_id": student.id,
                "student_code": student.student_code,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "full_name": student.full_name,
                "phone_number": student.phone_number,
                "is_active": student.is_active,
                "total_reservations": student.total_reservations,
                "cancelled_count": student.cancelled_count,
                "used_count": student.used_count,
                "no_show_count": student.no_show_count,
                "active_reservations": student.active_reservations,
            }
        )
    students_with_reservations = sum(1 for item in results if item["total_reservations"] > 0)
    total_students = len(results)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "summary": {
            "total_students": total_students,
            "active_students": sum(1 for item in results if item["is_active"]),
            "students_with_reservations": students_with_reservations,
            "total_reservations": sum(item["total_reservations"] for item in results),
            "participation_rate": _calculate_utilization(
                reserved_count=students_with_reservations,
                capacity=total_students,
            ),
        },
        "results": results,
    }


def get_meal_report(*, start_date=None, end_date=None):
    start_date, end_date = _resolve_report_range(start_date=start_date, end_date=end_date)
    schedules = MealSchedule.objects.select_related("meal")
    if start_date and end_date:
        schedules = schedules.filter(date__range=(start_date, end_date))

    schedules = schedules.annotate(
        total_reservation_count=Count("reservations"),
        occupied_count=Count(
            "reservations",
            filter=Q(reservations__status__in=OCCUPIED_STATUSES),
        ),
        cancelled_count=Count(
            "reservations",
            filter=Q(reservations__status=ReservationStatus.CANCELLED),
        ),
        used_count=Count(
            "reservations",
            filter=Q(reservations__status=ReservationStatus.USED),
        ),
        no_show_count=Count(
            "reservations",
            filter=Q(reservations__status=ReservationStatus.NO_SHOW),
        ),
    )

    per_meal = defaultdict(list)
    for schedule in schedules.order_by("date", "meal__name"):
        per_meal[schedule.meal_id].append(schedule)

    results = []
    for meal in Meal.objects.order_by("name"):
        meal_schedules = per_meal.get(meal.id, [])
        total_reservation_counts = [item.total_reservation_count for item in meal_schedules]
        occupied_counts = [item.occupied_count for item in meal_schedules]
        total_capacity = sum(item.capacity for item in meal_schedules)
        total_reservations = sum(total_reservation_counts)
        results.append(
            {
                "meal_id": meal.id,
                "meal_name": meal.name,
                "meal_code": meal.code,
                "service_count": len(meal_schedules),
                "total_reservations": total_reservations,
                "average_reservations": round(total_reservations / len(meal_schedules), 2)
                if meal_schedules
                else 0.0,
                "max_reservations": max(total_reservation_counts) if total_reservation_counts else 0,
                "min_reservations": min(total_reservation_counts) if total_reservation_counts else 0,
                "cancelled_count": sum(item.cancelled_count for item in meal_schedules),
                "used_count": sum(item.used_count for item in meal_schedules),
                "no_show_count": sum(item.no_show_count for item in meal_schedules),
                "capacity": total_capacity,
                "utilization_percentage": _calculate_utilization(
                    reserved_count=total_reservations,
                    capacity=total_capacity,
                ),
            }
        )
    return {
        "start_date": start_date,
        "end_date": end_date,
        "summary": {
            "meal_count": len(results),
            "scheduled_meals": sum(item["service_count"] for item in results),
            "total_reservations": sum(item["total_reservations"] for item in results),
            "total_capacity": sum(item["capacity"] for item in results),
        },
        "results": results,
    }


def get_reservation_report(*, start_date=None, end_date=None):
    start_date, end_date = _resolve_report_range(start_date=start_date, end_date=end_date)
    queryset = Reservation.objects.select_related("meal_schedule", "meal_schedule__meal")
    if start_date and end_date:
        queryset = queryset.filter(meal_schedule__date__range=(start_date, end_date))

    summary = queryset.aggregate(
        total_reservations=Count("id"),
        reserved_count=Count("id", filter=Q(status=ReservationStatus.RESERVED)),
        cancelled_count=Count("id", filter=Q(status=ReservationStatus.CANCELLED)),
        used_count=Count("id", filter=Q(status=ReservationStatus.USED)),
        no_show_count=Count("id", filter=Q(status=ReservationStatus.NO_SHOW)),
    )

    daily_queryset = MealSchedule.objects.all()
    if start_date and end_date:
        daily_queryset = daily_queryset.filter(date__range=(start_date, end_date))

    daily_rows = list(
        daily_queryset.values("date").annotate(
            reservation_count=Count(
                "reservations",
                filter=Q(reservations__status__in=OCCUPIED_STATUSES),
            )
        ).order_by("date")
    )

    status_breakdown = [
        {"status": ReservationStatus.RESERVED, "count": summary["reserved_count"]},
        {"status": ReservationStatus.CANCELLED, "count": summary["cancelled_count"]},
        {"status": ReservationStatus.USED, "count": summary["used_count"]},
        {"status": ReservationStatus.NO_SHOW, "count": summary["no_show_count"]},
    ]

    return {
        "start_date": start_date,
        "end_date": end_date,
        "summary": summary,
        "daily_reservations": daily_rows,
        "status_breakdown": status_breakdown,
    }


def _stringify_cell(value):
    if isinstance(value, float):
        return f"{value:.2f}"
    return "" if value is None else str(value)


def _build_csv_response(
    *,
    filename: str,
    title: str,
    range_label: str,
    headers: list[str],
    rows: list[list],
):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow([title])
    writer.writerow(["تاریخ تولید", timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M")])
    writer.writerow(["بازه گزارش", range_label])
    writer.writerow([])
    writer.writerow(headers)
    for row in rows:
        writer.writerow([_stringify_cell(value) for value in row])
    response = HttpResponse(
        f"\ufeff{buffer.getvalue()}",
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    return response


def _build_excel_response(
    *,
    filename: str,
    title: str,
    range_label: str,
    sheet_name: str,
    headers: list[str],
    rows: list[list],
):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_name
    worksheet.append([title])
    worksheet.append(["تاریخ تولید", timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M")])
    worksheet.append(["بازه گزارش", range_label])
    worksheet.append([])
    worksheet.append(headers)
    for row in rows:
        worksheet.append(row)

    worksheet["A1"].font = Font(size=14, bold=True)
    worksheet["A1"].alignment = Alignment(horizontal="right")
    header_fill = PatternFill("solid", fgColor="1F4B99")
    for cell in worksheet[5]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    worksheet.freeze_panes = "A6"
    for column_cells in worksheet.columns:
        first_cell = column_cells[0]
        if not first_cell.column_letter:
            continue
        max_length = max(len(_stringify_cell(cell.value)) for cell in column_cells if cell.value is not None)
        worksheet.column_dimensions[first_cell.column_letter].width = min(max(max_length + 2, 14), 32)

    buffer = BytesIO()
    workbook.save(buffer)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    return response


def _build_pdf_response(*, filename: str, title: str, range_label: str, headers: list[str], rows: list[list]):
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()

    table_rows = [headers]
    for row in rows:
        table_rows.append([_stringify_cell(value) for value in row])

    table = Table(table_rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    document.build(
        [
            Paragraph(title, styles["Title"]),
            Spacer(1, 6),
            Paragraph(f"Generated At: {timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
            Paragraph(f"Range: {range_label}", styles["Normal"]),
            Spacer(1, 12),
            table,
        ]
    )
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response


def export_report(
    *,
    filename: str,
    title: str,
    sheet_name: str,
    headers: list[str],
    rows: list[list],
    export_format: str,
    start_date=None,
    end_date=None,
):
    range_label = _format_report_range(start_date=start_date, end_date=end_date)
    if export_format == "csv":
        return _build_csv_response(
            filename=filename,
            title=title,
            range_label=range_label,
            headers=headers,
            rows=rows,
        )
    if export_format == "xlsx":
        return _build_excel_response(
            filename=filename,
            title=title,
            range_label=range_label,
            sheet_name=sheet_name,
            headers=headers,
            rows=rows,
        )
    return _build_pdf_response(
        filename=filename,
        title=title,
        range_label=range_label,
        headers=headers,
        rows=rows,
    )
