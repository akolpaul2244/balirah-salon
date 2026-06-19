from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit

from .forms import AppointmentForm, AppointmentCancelForm
from .models import Appointment, TimeSlot, AppointmentCancellation, BlockedSlot
from .services import get_available_slots, create_appointment
from apps.notifications.tasks import send_appointment_confirmation


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = create_appointment(form.cleaned_data, request.user)
            send_appointment_confirmation.delay(appointment.id)
            messages.success(
                request,
                f'Appointment booked! Your reference is {appointment.reference}. '
                f'A confirmation will be sent to you shortly.'
            )
            return redirect('bookings:confirmation', reference=appointment.reference)
    else:
        initial = {}
        service_id = request.GET.get('service')
        if service_id:
            initial['service'] = service_id
        form = AppointmentForm(initial=initial, user=request.user)
    return render(request, 'bookings/book_appointment.html', {'form': form})


def appointment_confirmation(request, reference):
    appointment = get_object_or_404(Appointment, reference=reference)
    if appointment.user and appointment.user != request.user and not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, 'bookings/confirmation.html', {'appointment': appointment})


@require_GET
def available_slots(request):
    service_id = request.GET.get('service')
    stylist_id = request.GET.get('stylist')
    date_str = request.GET.get('date')
    if not (service_id and date_str):
        return JsonResponse({'error': 'service and date are required'}, status=400)
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    if date < timezone.localdate():
        return JsonResponse({'slots': []})
    slots = get_available_slots(service_id, date, stylist_id or None)
    return JsonResponse({'slots': slots})


@require_GET
def stylist_availability(request):
    service_id = request.GET.get('service')
    date_str = request.GET.get('date')
    if not (service_id and date_str):
        return JsonResponse({'error': 'service and date are required'}, status=400)
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    from apps.team.models import Stylist
    from apps.services.models import Service
    try:
        service = Service.objects.get(pk=service_id, is_active=True)
    except Service.DoesNotExist:
        return JsonResponse({'stylists': []})
    stylists = Stylist.objects.filter(
        is_active=True,
        specializations=service.category,
    ).distinct()
    data = []
    for stylist in stylists:
        slots = get_available_slots(service_id, date, stylist.id)
        data.append({
            'id': stylist.id,
            'name': stylist.get_full_name(),
            'available_slots': len(slots),
        })
    return JsonResponse({'stylists': data})


@login_required
def cancel_appointment(request, reference):
    appointment = get_object_or_404(Appointment, reference=reference, user=request.user)
    if not appointment.can_cancel:
        messages.error(request, 'This appointment can no longer be cancelled.')
        return redirect('accounts:profile')
    if request.method == 'POST':
        form = AppointmentCancelForm(request.POST)
        if form.is_valid():
            appointment.status = 'cancelled'
            appointment.save(update_fields=['status'])
            AppointmentCancellation.objects.create(
                appointment=appointment,
                cancelled_by=request.user,
                reason=form.cleaned_data.get('reason', ''),
            )
            if appointment.time_slot:
                appointment.time_slot.is_available = True
                appointment.time_slot.save(update_fields=['is_available'])
            from apps.notifications.tasks import send_cancellation_notification
            send_cancellation_notification.delay(appointment.id)
            messages.success(request, f'Appointment {reference} has been cancelled.')
            return redirect('accounts:profile')
    else:
        form = AppointmentCancelForm()
    return render(request, 'bookings/cancel_appointment.html', {
        'appointment': appointment,
        'form': form,
    })


def appointment_detail(request, reference):
    appointment = get_object_or_404(Appointment, reference=reference)
    if appointment.user and appointment.user != request.user and not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, 'bookings/appointment_detail.html', {'appointment': appointment})
