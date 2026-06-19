import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'balirah_salon.settings.production')

app = Celery('balirah_salon')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-appointment-reminders': {
        'task': 'apps.notifications.tasks.send_appointment_reminders',
        'schedule': crontab(minute='*/30'),
    },
    'send-reengagement-sms': {
        'task': 'apps.notifications.tasks.send_reengagement_sms',
        'schedule': crontab(hour=9, minute=0),
    },
    'send-birthday-promotions': {
        'task': 'apps.notifications.tasks.send_birthday_promotions',
        'schedule': crontab(hour=8, minute=0),
    },
    'cleanup-expired-slots': {
        'task': 'apps.bookings.tasks.cleanup_expired_slots',
        'schedule': crontab(hour=0, minute=0),
    },
}
