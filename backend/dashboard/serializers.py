from rest_framework import serializers


class DashboardDateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"detail": "start_date must be less than or equal to end_date."})
        return attrs


class ReservationsByDayPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    reservation_count = serializers.IntegerField()


class PopularMealPointSerializer(serializers.Serializer):
    meal_id = serializers.IntegerField()
    meal_name = serializers.CharField()
    total_reservations = serializers.IntegerField()


class CapacityVsReservationPointSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    date = serializers.DateField()
    meal_id = serializers.IntegerField()
    meal_name = serializers.CharField()
    capacity = serializers.IntegerField()
    reservation_count = serializers.IntegerField()
    remaining_capacity = serializers.IntegerField()


class DailyReservationPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    reservation_count = serializers.IntegerField()


class CancelledReservationPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    cancelled_count = serializers.IntegerField()


class DashboardChartsSerializer(serializers.Serializer):
    reservations_by_day = ReservationsByDayPointSerializer(many=True)
    popular_meals = PopularMealPointSerializer(many=True)
    capacity_vs_reservations = CapacityVsReservationPointSerializer(many=True)
    daily_reservations = DailyReservationPointSerializer(many=True)
    cancelled_reservations = CancelledReservationPointSerializer(many=True)


class DashboardResponseSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    charts = DashboardChartsSerializer()
