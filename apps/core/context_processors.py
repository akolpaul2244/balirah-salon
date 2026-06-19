from django.conf import settings
from django.core.cache import cache
from .models import SalonSettings, OpeningHours


def salon_context(request):
    salon = cache.get('salon_settings')
    if salon is None:
        salon = SalonSettings.get()
        cache.set('salon_settings', salon, 60 * 60)

    opening_hours = cache.get('opening_hours')
    if opening_hours is None:
        opening_hours = list(OpeningHours.objects.all())
        cache.set('opening_hours', opening_hours, 60 * 60)

    return {
        'salon': salon,
        'opening_hours': opening_hours,
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', ''),
        'salon_phone': getattr(settings, 'SALON_PHONE', ''),
    }
