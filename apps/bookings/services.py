from datetime import datetime, time, timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import TimeSlot, Appointment, BlockedSlot
from apps.services.models import Service
from apps.team.models import Stylist


def get_available_slots(service_id, date, stylist_id=None):
    try:
        service = Service.objects.get(pk=service_id, is_active=True)
    except Service.DoesNotExist:
        return []

    duration = service.duration_minutes
    slot_size = settings.BOOKING_SLOT_DURATION

    stylists = Stylist.objects.filter(is_active=True, specializations=service.category)
    if stylist_id:
        stylists = stylists.filter(pk=stylist_id)

    if not stylists.exists():
        return []

    booked_slots = set(
        TimeSlot.objects.filter(
            stylist__in=stylists,
            date=date,
            is_available=False,
        ).values_list('start_time', flat=True)
    )

    blocked = BlockedSlot.objects.filter(stylist__in=stylists, date=date)

    working_hours = _get_working_hours(date)
    slots = []
    for start in _generate_slot_times(working_hours['open'], working_hours['close'], slot_size):
        end = _add_minutes(start, duration)
        if end > working_hours['close']:
            break
        if _slot_is_blocked(start, end, blocked):
            continue
        existing = TimeSlot.objects.filter(
            stylist__in=stylists,
            date=date,
            start_time=start,
            is_available=True,
        ).first()
        if existing or start not in booked_slots:
            slot_id = existing.id if existing else None
            slots.append({
                'id': slot_id,
                'start': start.strftime('%H:%M'),
                'end': end.strftime('%H:%M'),
                'available': True,
            })
    return slots


def _get_working_hours(date):
    weekday = date.weekday()
    if weekday == 6:
        return {'open': time(9, 0), 'close': time(17, 0)}
    return {'open': time(8, 0), 'close': time(20, 0)}


def _generate_slot_times(open_time, close_time, interval_minutes):
    slots = []
    current = datetime.combine(datetime.today(), open_time)
    close = datetime.combine(datetime.today(), close_time)
    while current < close:
        slots.append(current.time())
        current += timedelta(minutes=interval_minutes)
    return slots


def _add_minutes(t, minutes):
    dt = datetime.combine(datetime.today(), t) + timedelta(minutes=minutes)
    return dt.time()


def _slot_is_blocked(start, end, blocked_slots):
    for block in blocked_slots:
        if start < block.end_time and end > block.start_time:
            return True
    return False


@transaction.atomic
def create_appointment(data, user=None):
    slot_obj = data.get('time_slot_obj')
    service = data['service']
    stylist = data.get('stylist')

    if slot_obj:
        if not slot_obj.is_available:
            from django.core.exceptions import ValidationError
            raise ValidationError('Time slot is no longer available.')
        slot_obj.is_available = False
        slot_obj.save(update_fields=['is_available'])
        actual_stylist = slot_obj.stylist
        date = slot_obj.date
        start = slot_obj.start_time
        end = _add_minutes(start, service.duration_minutes)
    else:
        actual_stylist = stylist
        date = data['appointment_date']
        start = data.get('start_time', time(9, 0))
        end = _add_minutes(start, service.duration_minutes)
        slot_obj, _ = TimeSlot.objects.get_or_create(
            stylist=actual_stylist,
            date=date,
            start_time=start,
            defaults={'end_time': end, 'is_available': False},
        )
        slot_obj.is_available = False
        slot_obj.save(update_fields=['is_available'])

    appointment_data = {
        'service': service,
        'stylist': actual_stylist,
        'time_slot': slot_obj,
        'appointment_date': date,
        'start_time': start,
        'end_time': end,
        'notes': data.get('notes', ''),
        'price_paid': service.price,
    }

    if user and user.is_authenticated:
        appointment_data['user'] = user
    else:
        appointment_data['guest_name'] = data.get('guest_name', '')
        appointment_data['guest_email'] = data.get('guest_email', '')
        appointment_data['guest_phone'] = data.get('guest_phone', '')

    return Appointment.objects.create(**appointment_data)
