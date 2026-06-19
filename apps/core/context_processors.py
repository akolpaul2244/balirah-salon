from django.conf import settings
from django.core.cache import cache
from django.db import connection
from .models import SalonSettings, OpeningHours


def _db_ready():
    try:
        connection.ensure_connection()
        return connection.introspection.table_names().__contains__('core_salonsettings')
    except Exception:
        return False


def salon_context(request):
    if not _db_ready():
        return {
            'salon': None,
            'opening_hours': [],
            'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', ''),
            'salon_phone': getattr(settings, 'SALON_PHONE', ''),
        }

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