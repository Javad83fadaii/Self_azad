from rest_framework import serializers


EXPORT_FORMAT_CHOICES = ("csv", "xlsx", "pdf")


class ExportFormatSerializerMixin(serializers.Serializer):
    export = serializers.ChoiceField(choices=EXPORT_FORMAT_CHOICES, required=False)


class DailyMealReportFilterSerializer(ExportFormatSerializerMixin):
    date = serializers.DateField()


class StudentReportFilterSerializer(ExportFormatSerializerMixin):
    student_code = serializers.CharField(required=False, allow_blank=False)
    first_name = serializers.CharField(required=False, allow_blank=False)
    last_name = serializers.CharField(required=False, allow_blank=False)
    phone_number = serializers.CharField(required=False, allow_blank=False)


class MealReportFilterSerializer(ExportFormatSerializerMixin):
    pass


class DailyMealReportItemSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    meal_id = serializers.IntegerField()
    meal_name = serializers.CharField()
    reservation_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    capacity = serializers.IntegerField()
    remaining_capacity = serializers.IntegerField()
    utilization_percentage = serializers.FloatField()


class DailyMealReportResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    results = DailyMealReportItemSerializer(many=True)


class StudentReportItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_code = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    total_reservations = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    used_count = serializers.IntegerField()
    no_show_count = serializers.IntegerField()
    active_reservations = serializers.IntegerField()


class StudentReportResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = StudentReportItemSerializer(many=True)


class MealReportItemSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField()
    meal_name = serializers.CharField()
    meal_code = serializers.CharField()
    total_reservations = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()
    used_count = serializers.IntegerField()
    no_show_count = serializers.IntegerField()
    capacity = serializers.IntegerField()
    utilization_percentage = serializers.FloatField()


class MealReportResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = MealReportItemSerializer(many=True)
