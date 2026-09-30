from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from audit_logs.models import AuditLog
from audit_logs.serializers import (
    AuditLogFilterSerializer,
    AuditLogItemSerializer,
    AuditLogListResponseSerializer,
)
from common.permissions import IsAdminRole


class AuditLogListView(APIView):
    """Return admin-only audit log rows with simple filters."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = AuditLogFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        queryset = AuditLog.objects.select_related("user")
        username = serializer.validated_data.get("username")
        action = serializer.validated_data.get("action")
        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")

        if username:
            queryset = queryset.filter(
                Q(user__username__icontains=username)
                | Q(user__first_name__icontains=username)
                | Q(user__last_name__icontains=username)
            )
        if action:
            queryset = queryset.filter(action__icontains=action)
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__range=(start_date, end_date))

        results = [
            {
                "id": item.id,
                "username": item.user.username if item.user else None,
                "full_name": item.user.get_full_name().strip() if item.user else None,
                "action": item.action,
                "description": item.description,
                "created_at": item.created_at,
            }
            for item in queryset.order_by("-created_at")
        ]
        response_serializer = AuditLogListResponseSerializer(
            data={
                "count": len(results),
                "results": results,
            }
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)
