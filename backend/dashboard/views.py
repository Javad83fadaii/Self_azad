from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole
from dashboard.serializers import DashboardDateRangeSerializer, DashboardResponseSerializer
from dashboard.services import get_dashboard_data


class DashboardAnalyticsView(APIView):
    """Return dashboard chart datasets for admin users."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = DashboardDateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = get_dashboard_data(**serializer.validated_data)
        response_serializer = DashboardResponseSerializer(data=data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)
