from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment, TimeSlot, BlockedSlot, AppointmentCancellation


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'client_name', 'service', 'stylist',
        'appointment_date', 'start_time', 'status_badge', 'created_at'
    )
    list_filter = ('status', 'appointment_date', 'service__category', 'stylist')
    search_fields = (
        'reference', 'user__email', 'user__first_name',
        'guest_name', 'guest_email', 'guest_phone'
    )
    readonly_fields = ('reference', 'created_at', 'updated_at')
    date_hierarchy = 'appointment_date'
    list_per_page = 30
    fieldsets = (
        ('Reference', {'fields': ('reference', 'status')}),
        ('Client', {'fields': ('user', 'guest_name', 'guest_email', 'guest_phone')}),
        ('Booking Details', {'fields': ('service', 'stylist', 'time_slot', 'appointment_date', 'start_time', 'end_time', 'notes')}),
        ('Payment', {'fields': ('price_paid',)}),
        ('Notifications', {'fields': ('confirmation_sent', 'reminder_24h_sent', 'reminder_2h_sent', 'reengagement_sent')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#007BFF',
            'in_progress': '#17A2B8',
            'completed': '#28A745',
            'cancelled': '#DC3545',
            'no_show': '#6C757D',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service', 'stylist')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('stylist', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('is_available', 'stylist', 'date')
    date_hierarchy = 'date'


@admin.register(BlockedSlot)
class BlockedSlotAdmin(admin.ModelAdmin):
    list_display = ('stylist', 'date', 'start_time', 'end_time', 'reason')
    list_filter = ('stylist',)
    date_hierarchy = 'date'


@admin.register(AppointmentCancellation)
class AppointmentCancellationAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'cancelled_by', 'cancelled_at')
    readonly_fields = ('cancelled_at',)
