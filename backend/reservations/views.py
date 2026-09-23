from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole, IsStudentRole
from reservations.models import Reservation
from reservations.serializers import (
    ReservationByDateFilterSerializer,
    ReservationByMealFilterSerializer,
    ReservationCreateSerializer,
    ReservationSerializer,
)
from reservations.services import (
    cancel_reservation,
    create_reservation,
    list_admin_reservations,
    list_student_reservations,
)


class ReservationCreateView(APIView):
    """Create a reservation for the authenticated student."""

    permission_classes = [IsStudentRole]

    def post(self, request, *args, **kwargs):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = create_reservation(
            student=request.user.student_profile,
            **serializer.validated_data,
        )
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)


class MyReservationListView(APIView):
    """List reservations that belong to the authenticated student only."""

    permission_classes = [IsStudentRole]

    def get(self, request, *args, **kwargs):
        queryset = list_student_reservations(student=request.user.student_profile)
        return Response(ReservationSerializer(queryset, many=True).data)


class ReservationCancelView(APIView):
    """Cancel one of the authenticated student's active reservations."""

    permission_classes = [IsStudentRole]

    def delete(self, request, pk, *args, **kwargs):
        reservation = get_object_or_404(Reservation, pk=pk, student=request.user.student_profile)
        reservation = cancel_reservation(reservation=reservation)
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)


class ReservationListView(APIView):
    """List all reservations for admin users."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        queryset = list_admin_reservations()
        return Response(ReservationSerializer(queryset, many=True).data)


class ReservationByDateListView(APIView):
    """Filter reservations by schedule date for admin users."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = ReservationByDateFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        queryset = list_admin_reservations(reservation_date=serializer.validated_data["date"])
        return Response(ReservationSerializer(queryset, many=True).data)


class ReservationByMealListView(APIView):
    """Filter reservations by meal for admin users."""

    permission_classes = [IsAdminRole]

    def get(self, request, *args, **kwargs):
        serializer = ReservationByMealFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        queryset = list_admin_reservations(meal_id=serializer.validated_data["meal_id"])
        return Response(ReservationSerializer(queryset, many=True).data)
