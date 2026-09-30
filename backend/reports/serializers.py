from rest_framework import serializers


EXPORT_FORMAT_CHOICES = ("csv", "xlsx", "pdf")


class ExportFormatSerializerMixin(serializers.Serializer):
    export = serializers.ChoiceField(choices=EXPORT_FORMAT_CHOICES, required=False)


class DateRangeFilterSerializerMixin(serializers.Serializer):
    date = serializers.DateField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    require_date_range = False

    def validate(self, attrs):
        date = attrs.get("date")
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if date is not None:
            attrs["start_date"] = date
            attrs["end_date"] = date
            return attrs

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"detail": "start_date must be less than or equal to end_date."})

        if start_date and not end_date:
            attrs["end_date"] = start_date
        elif end_date and not start_date:
            attrs["start_date"] = end_date

        if self.require_date_range and not attrs.get("start_date") and not attrs.get("end_date"):
            raise serializers.ValidationError({"date": "date or start_date/end_date is required."})

        return attrs


class DailyMealReportFilterSerializer(ExportFormatSerializerMixin, DateRangeFilterSerializerMixin):
    require_date_range = True


class StudentReportFilterSerializer(ExportFormatSerializerMixin, DateRangeFilterSerializerMixin):
    student_code = serializers.CharField(required=False, allow_blank=False)
    first_name = serializers.CharField(required=False, allow_blank=False)
    last_name = serializers.CharField(required=False, allow_blank=False)
    phone_number = serializers.CharField(required=False, allow_blank=False)


class MealReportFilterSerializer(ExportFormatSerializerMixin, DateRangeFilterSerializerMixin):
    pass


class ReservationReportFilterSerializer(ExportFormatSerializerMixin, DateRangeFilterSerializerMixin):
    pass


class DailyMealReportItemSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    date = serializers.DateField()
    meal_id = serializers.IntegerField()
    meal_name = serializers.CharField()
    reservation_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    capacity = serializers.IntegerField()
    remaining_capacity = serializers.IntegerField()
    utilization_percentage = serializers.FloatField()


class DailyMealReportResponseSerializer(serializers.Serializer):
    date = serializers.DateField(required=False, allow_null=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    count = serializers.IntegerField()
    results = DailyMealReportItemSerializer(many=True)


class StudentReportItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_code = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    is_active = serializers.BooleanField()
    total_reservations = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    used_count = serializers.IntegerField()
    no_show_count = serializers.IntegerField()
    active_reservations = serializers.IntegerField()


class StudentReportSummarySerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    students_with_reservations = serializers.IntegerField()
    total_reservations = serializers.IntegerField()
    participation_rate = serializers.FloatField()


class StudentReportResponseSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    count = serializers.IntegerField()
    summary = StudentReportSummarySerializer()
    results = StudentReportItemSerializer(many=True)


class MealReportItemSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField()
    meal_name = serializers.CharField()
    meal_code = serializers.CharField()
    service_count = serializers.IntegerField()
    total_reservations = serializers.IntegerField()
    average_reservations = serializers.FloatField()
    max_reservations = serializers.IntegerField()
    min_reservations = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    used_count = serializers.IntegerField()
    no_show_count = serializers.IntegerField()
    capacity = serializers.IntegerField()
    utilization_percentage = serializers.FloatField()


class MealReportSummarySerializer(serializers.Serializer):
    meal_count = serializers.IntegerField()
    scheduled_meals = serializers.IntegerField()
    total_reservations = serializers.IntegerField()
    total_capacity = serializers.IntegerField()


class MealReportResponseSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    count = serializers.IntegerField()
    summary = MealReportSummarySerializer()
    results = MealReportItemSerializer(many=True)


class ReservationStatusItemSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class ReservationDailyItemSerializer(serializers.Serializer):
    date = serializers.DateField()
    reservation_count = serializers.IntegerField()


class ReservationReportSummarySerializer(serializers.Serializer):
    total_reservations = serializers.IntegerField()
    reserved_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    used_count = serializers.IntegerField()
    no_show_count = serializers.IntegerField()


class ReservationReportResponseSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    summary = ReservationReportSummarySerializer()
    daily_reservations = ReservationDailyItemSerializer(many=True)
    status_breakdown = ReservationStatusItemSerializer(many=True)
