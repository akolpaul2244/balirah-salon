from celery import shared_task
from django.utils import timezone


@shared_task
def cleanup_expired_slots():
    from .models import TimeSlot
    yesterday = timezone.localdate() - timezone.timedelta(days=1)
    deleted, _ = TimeSlot.objects.filter(date__lt=yesterday).delete()
    return f'Deleted {deleted} expired time slots'
