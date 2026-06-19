from rest_framework import serializers
from .models import Appointment, TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'date', 'start_time', 'end_time', 'is_available']


class AppointmentSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    stylist_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'reference', 'service_name', 'stylist_name',
            'appointment_date', 'start_time', 'end_time',
            'status', 'status_display', 'notes', 'created_at',
        ]
        read_only_fields = ['reference', 'created_at']

    def get_stylist_name(self, obj):
        return obj.stylist.get_full_name()
