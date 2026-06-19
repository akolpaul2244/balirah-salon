from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import Appointment
from .serializers import AppointmentSerializer
from .services import get_available_slots


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Appointment.objects.filter(
            user=self.request.user
        ).select_related('service', 'stylist').order_by('-appointment_date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()
        if not appointment.can_cancel:
            return Response(
                {'detail': 'This appointment can no longer be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        appointment.status = 'cancelled'
        appointment.save(update_fields=['status'])
        if appointment.time_slot:
            appointment.time_slot.is_available = True
            appointment.time_slot.save(update_fields=['is_available'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailableSlotsView(APIView):
    permission_classes = []

    def get(self, request):
        service_id = request.query_params.get('service')
        stylist_id = request.query_params.get('stylist')
        date_str = request.query_params.get('date')

        if not service_id or not date_str:
            return Response({'error': 'service and date are required'}, status=400)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        if date < timezone.localdate():
            return Response({'slots': []})

        slots = get_available_slots(service_id, date, stylist_id)
        return Response({'slots': slots})
