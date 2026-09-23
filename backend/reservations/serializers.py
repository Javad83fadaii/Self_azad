from rest_framework import serializers

from reservations.models import Reservation, ReservationStatus


class ReservationSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source="student.id", read_only=True)
    student_code = serializers.CharField(source="student.student_code", read_only=True)
    meal_schedule_id = serializers.IntegerField(source="meal_schedule.id", read_only=True)
    meal_id = serializers.IntegerField(source="meal_schedule.meal.id", read_only=True)
    meal_name = serializers.CharField(source="meal_schedule.meal.name", read_only=True)
    schedule_date = serializers.DateField(source="meal_schedule.date", read_only=True)

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
            "schedule_date",
            "reservation_date",
            "status",
            "created_at",
            "cancelled_at",
        ]


class ReservationCreateSerializer(serializers.Serializer):
    meal_schedule_id = serializers.IntegerField()


class ReservationCancelSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ReservationStatus.choices, read_only=True)


class ReservationByDateFilterSerializer(serializers.Serializer):
    date = serializers.DateField()


class ReservationByMealFilterSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField(min_value=1)
