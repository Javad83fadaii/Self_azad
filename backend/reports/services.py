from __future__ import annotations

import csv
from io import BytesIO, StringIO

from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from openpyxl import Workbook
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


def get_daily_meal_report(*, date):
    schedules = (
        MealSchedule.objects.select_related("meal")
        .filter(date=date)
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
    student_code: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    phone_number: str | None = None,
):
    queryset = Student.objects.select_related("user").annotate(
        total_reservations=Count("reservations"),
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
        active_reservations=Count(
            "reservations",
            filter=Q(reservations__status=ReservationStatus.RESERVED),
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
                "total_reservations": student.total_reservations,
                "cancelled_count": student.cancelled_count,
                "used_count": student.used_count,
                "no_show_count": student.no_show_count,
                "active_reservations": student.active_reservations,
            }
        )
    return results


def get_meal_report():
    capacities = {
        item["meal_id"]: item["capacity"]
        for item in MealSchedule.objects.values("meal_id").annotate(capacity=Sum("capacity"))
    }
    reservation_stats = {
        item["meal_schedule__meal_id"]: item
        for item in Reservation.objects.values("meal_schedule__meal_id").annotate(
            total_reservations=Count("id"),
            cancelled_count=Count("id", filter=Q(status=ReservationStatus.CANCELLED)),
            used_count=Count("id", filter=Q(status=ReservationStatus.USED)),
            no_show_count=Count("id", filter=Q(status=ReservationStatus.NO_SHOW)),
            occupied_count=Count("id", filter=Q(status__in=OCCUPIED_STATUSES)),
        )
    }

    results = []
    for meal in Meal.objects.order_by("name"):
        stats = reservation_stats.get(meal.id, {})
        capacity = capacities.get(meal.id, 0) or 0
        occupied_count = stats.get("occupied_count", 0)
        results.append(
            {
                "meal_id": meal.id,
                "meal_name": meal.name,
                "meal_code": meal.code,
                "total_reservations": stats.get("total_reservations", 0),
                "cancelled_count": stats.get("cancelled_count", 0),
                "used_count": stats.get("used_count", 0),
                "no_show_count": stats.get("no_show_count", 0),
                "capacity": capacity,
                "utilization_percentage": _calculate_utilization(
                    reserved_count=occupied_count,
                    capacity=capacity,
                ),
            }
        )
    return results


def _stringify_cell(value):
    if isinstance(value, float):
        return f"{value:.2f}"
    return "" if value is None else str(value)


def _build_csv_response(*, filename: str, headers: list[str], rows: list[list]):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([_stringify_cell(value) for value in row])
    response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    return response


def _build_excel_response(*, filename: str, sheet_name: str, headers: list[str], rows: list[list]):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_name
    worksheet.append(headers)
    for row in rows:
        worksheet.append(row)

    buffer = BytesIO()
    workbook.save(buffer)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    return response


def _build_pdf_response(*, filename: str, title: str, headers: list[str], rows: list[list]):
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

    document.build([Paragraph(title, styles["Title"]), Spacer(1, 12), table])
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response


def export_report(*, filename: str, title: str, sheet_name: str, headers: list[str], rows: list[list], export_format: str):
    if export_format == "csv":
        return _build_csv_response(filename=filename, headers=headers, rows=rows)
    if export_format == "xlsx":
        return _build_excel_response(filename=filename, sheet_name=sheet_name, headers=headers, rows=rows)
    return _build_pdf_response(filename=filename, title=title, headers=headers, rows=rows)
