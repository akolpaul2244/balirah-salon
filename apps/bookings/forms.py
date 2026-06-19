from django import forms
from django.utils import timezone
from .models import Appointment
from apps.services.models import Service
from apps.team.models import Stylist


class AppointmentForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).select_related('category'),
        empty_label='Select a service',
    )
    stylist = forms.ModelChoiceField(
        queryset=Stylist.objects.filter(is_active=True),
        empty_label='Any Available Stylist',
        required=False,
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    time_slot = forms.IntegerField(widget=forms.HiddenInput())
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        max_length=500,
    )

    guest_name = forms.CharField(max_length=200, required=False)
    guest_email = forms.EmailField(required=False)
    guest_phone = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if not user or not user.is_authenticated:
            self.fields['guest_name'].required = True
            self.fields['guest_phone'].required = True

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date < timezone.localdate():
            raise forms.ValidationError('Appointment date cannot be in the past.')
        if date and (date - timezone.localdate()).days > 30:
            raise forms.ValidationError('Appointments can only be booked up to 30 days in advance.')
        return date

    def clean_guest_phone(self):
        phone = self.cleaned_data.get('guest_phone', '')
        if phone and not phone.startswith('+'):
            phone = '+256' + phone.lstrip('0')
        return phone

    def clean(self):
        cleaned = super().clean()
        from .models import TimeSlot
        slot_id = cleaned.get('time_slot')
        if slot_id:
            try:
                slot = TimeSlot.objects.get(pk=slot_id, is_available=True)
                cleaned['time_slot_obj'] = slot
            except TimeSlot.DoesNotExist:
                raise forms.ValidationError('Selected time slot is no longer available.')
        return cleaned


class AppointmentCancelForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        max_length=500,
        label='Reason for cancellation (optional)',
    )
