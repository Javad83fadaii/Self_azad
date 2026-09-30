from rest_framework import serializers


class AuditLogFilterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=False)
    action = serializers.CharField(required=False, allow_blank=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({"detail": "start_date must be less than or equal to end_date."})
        if start_date and not end_date:
            attrs["end_date"] = start_date
        elif end_date and not start_date:
            attrs["start_date"] = end_date
        return attrs


class AuditLogItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(allow_null=True)
    full_name = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField()


class AuditLogListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = AuditLogItemSerializer(many=True)
