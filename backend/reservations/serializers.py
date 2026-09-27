from rest_framework import serializers

from reservations.models import Reservation, ReservationStatus


class ReservationSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source="student.id", read_only=True)
    student_code = serializers.CharField(source="student.student_code", read_only=True)
    meal_schedule_id = serializers.IntegerField(source="meal_schedule.id", read_only=True)
    meal_id = serializers.IntegerField(source="meal_schedule.meal.id", read_only=True)
    meal_name = serializers.CharField(source="meal_schedule.meal.name", read_only=True)
    meal_code = serializers.CharField(source="meal_schedule.meal.code", read_only=True)
    meal_image_url = serializers.SerializerMethodField()
    schedule_date = serializers.DateField(source="meal_schedule.date", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            "id",
            "reservation_code",
            "student_id",
            "student_code",
            "meal_schedule_id",
            "meal_id",
            "meal_name",
            "meal_code",
            "meal_image_url",
            "schedule_date",
            "reservation_date",
            "status",
            "status_label",
            "can_cancel",
            "created_at",
            "cancelled_at",
        ]

    def get_meal_image_url(self, obj: Reservation) -> str:
        image = getattr(obj.meal_schedule.meal, "image", None)
        if image and getattr(image, "name", ""):
            return image.url
        return ""

    def get_can_cancel(self, obj: Reservation) -> bool:
        return obj.status == ReservationStatus.RESERVED


class ReservationCreateSerializer(serializers.Serializer):
    meal_schedule_id = serializers.IntegerField()


class ReservationCancelSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ReservationStatus.choices, read_only=True)


class ReservationByDateFilterSerializer(serializers.Serializer):
    date = serializers.DateField()


class ReservationByMealFilterSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(min_value=1)
