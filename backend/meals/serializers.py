from rest_framework import serializers

from meals.models import Meal, MealSchedule


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = [
            "id",
            "name",
            "code",
            "description",
            "image",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        ]


class MealScheduleSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    meal_id = serializers.PrimaryKeyRelatedField(
        source="meal",
        queryset=Meal.objects.all(),
        write_only=True,
    )
    reserved_count = serializers.IntegerField(read_only=True)
    remaining_capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = MealSchedule
        fields = [
            "id",
            "meal",
            "meal_id",
            "date",
            "capacity",
            "reserved_count",
            "remaining_capacity",
            "reservation_open_at",
            "reservation_close_at",
            "is_active",
            "created_at",
            "updated_at",
        ]
