from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.services.models import Service
from apps.team.models import Stylist


class TimeSlot(models.Model):
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('stylist', 'date', 'start_time')
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['stylist', 'date', 'is_available']),
            models.Index(fields=['date', 'is_available']),
        ]

    def __str__(self):
        return f'{self.stylist} – {self.date} {self.start_time}'


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='appointments'
    )
    guest_name = models.CharField(max_length=200, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='appointments')
    stylist = models.ForeignKey(Stylist, on_delete=models.PROTECT, related_name='appointments')
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.PROTECT, related_name='appointment')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reminder_24h_sent = models.BooleanField(default=False)
    reminder_2h_sent = models.BooleanField(default=False)
    reengagement_sent = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    reference = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-start_time']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stylist', 'appointment_date']),
            models.Index(fields=['status', 'appointment_date']),
            models.Index(fields=['reminder_24h_sent', 'reminder_2h_sent']),
        ]

    def __str__(self):
        client = self.user.get_full_name() if self.user else self.guest_name
        return f'{self.reference} – {client} – {self.service.name}'

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        import random
        import string
        prefix = 'BAL'
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        return f'{prefix}{suffix}'

    @property
    def client_name(self):
        if self.user:
            return self.user.get_full_name()
        return self.guest_name

    @property
    def client_phone(self):
        if self.user:
            return self.user.phone_number
        return self.guest_phone

    @property
    def client_email(self):
        if self.user:
            return self.user.email
        return self.guest_email

    @property
    def is_upcoming(self):
        now = timezone.now()
        appt_dt = timezone.make_aware(
            timezone.datetime.combine(self.appointment_date, self.start_time)
        )
        return appt_dt > now and self.status in ('pending', 'confirmed')

    @property
    def can_cancel(self):
        from datetime import timedelta
        cancel_limit = settings.BOOKING_CANCEL_HOURS
        now = timezone.now()
        appt_dt = timezone.make_aware(
            timezone.datetime.combine(self.appointment_date, self.start_time)
        )
        return appt_dt - now > timedelta(hours=cancel_limit) and self.status in ('pending', 'confirmed')


class AppointmentCancellation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='cancellation')
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='cancellations'
    )
    reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cancellation for {self.appointment.reference}'


class BlockedSlot(models.Model):
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE, related_name='blocked_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.stylist} blocked {self.date} {self.start_time}–{self.end_time}'
