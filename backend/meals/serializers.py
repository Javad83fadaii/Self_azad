from django.utils import timezone
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
    meal_name = serializers.CharField(source="meal.name", read_only=True)
    meal_code = serializers.CharField(source="meal.code", read_only=True)
    meal_description = serializers.CharField(source="meal.description", read_only=True)
    meal_image_url = serializers.SerializerMethodField()
    reserved_count = serializers.IntegerField(read_only=True, source="_reserved_count")
    remaining_capacity = serializers.IntegerField(read_only=True, source="_remaining_capacity")
    reservation_state = serializers.SerializerMethodField()
    is_reservable = serializers.SerializerMethodField()

    class Meta:
        model = MealSchedule
        fields = [
            "id",
            "meal",
            "meal_id",
            "meal_name",
            "meal_code",
            "meal_description",
            "meal_image_url",
            "date",
            "capacity",
            "reserved_count",
            "remaining_capacity",
            "reservation_open_at",
            "reservation_close_at",
            "reservation_state",
            "is_reservable",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_meal_image_url(self, obj: MealSchedule) -> str:
        image = getattr(obj.meal, "image", None)
        if image and getattr(image, "name", ""):
            return image.url
        return ""

    def get_reservation_state(self, obj: MealSchedule) -> str:
        now = timezone.localtime(timezone.now())
        remaining_capacity = getattr(obj, "_remaining_capacity", obj.remaining_capacity)

        if now < obj.reservation_open_at:
            return "NOT_OPEN"
        if now > obj.reservation_close_at:
            return "CLOSED"
        if remaining_capacity <= 0:
            return "FULL"
        return "AVAILABLE"

    def get_is_reservable(self, obj: MealSchedule) -> bool:
        return self.get_reservation_state(obj) == "AVAILABLE"
