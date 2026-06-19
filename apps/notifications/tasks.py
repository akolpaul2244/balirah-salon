import logging
from datetime import timedelta
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_confirmation(self, appointment_id):
    from apps.bookings.models import Appointment
    from .sms import send_sms
    from .email import send_email

    try:
        appt = Appointment.objects.select_related('service', 'stylist', 'user').get(pk=appointment_id)
    except Appointment.DoesNotExist:
        logger.warning(f'Appointment {appointment_id} not found for confirmation')
        return

    salon_name = settings.SALON_NAME
    date_str = appt.appointment_date.strftime('%A, %d %B %Y')
    time_str = appt.start_time.strftime('%I:%M %p')

    sms_message = (
        f'Hi {appt.client_name}, your appointment at {salon_name} is confirmed!\n'
        f'Service: {appt.service.name}\n'
        f'Date: {date_str} at {time_str}\n'
        f'Stylist: {appt.stylist.get_full_name()}\n'
        f'Ref: {appt.reference}'
    )

    phone = appt.client_phone
    if phone:
        send_sms(phone, sms_message, appointment=appt, sms_type='confirmation')

    email = appt.client_email
    if email:
        send_email(
            recipient=email,
            subject=f'Appointment Confirmed – {appt.reference} | {salon_name}',
            template_name='appointment_confirmation',
            context={'appointment': appt, 'salon_name': salon_name},
            appointment=appt,
            email_type='confirmation',
        )

    appt.confirmation_sent = True
    appt.save(update_fields=['confirmation_sent'])


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_appointment_reminders(self):
    from apps.bookings.models import Appointment
    from .sms import send_sms
    from .email import send_email

    now = timezone.now()
    salon_name = settings.SALON_NAME

    reminder_24h_start = now + timedelta(hours=23, minutes=30)
    reminder_24h_end = now + timedelta(hours=24, minutes=30)
    upcoming_24h = Appointment.objects.filter(
        status__in=('pending', 'confirmed'),
        reminder_24h_sent=False,
        appointment_date=reminder_24h_start.date(),
        start_time__range=(reminder_24h_start.time(), reminder_24h_end.time()),
    ).select_related('service', 'stylist', 'user')

    for appt in upcoming_24h:
        date_str = appt.appointment_date.strftime('%A, %d %B')
        time_str = appt.start_time.strftime('%I:%M %p')
        msg = (
            f'Reminder: Your {appt.service.name} appointment at {salon_name} is TOMORROW '
            f'({date_str}) at {time_str}. See you soon! Ref: {appt.reference}'
        )
        phone = appt.client_phone
        if phone:
            send_sms(phone, msg, appointment=appt, sms_type='reminder_24h')
        email = appt.client_email
        if email:
            send_email(
                recipient=email,
                subject=f'Reminder: Your appointment tomorrow – {salon_name}',
                template_name='appointment_reminder',
                context={'appointment': appt, 'salon_name': salon_name, 'hours': 24},
                appointment=appt,
                email_type='reminder_24h',
            )
        appt.reminder_24h_sent = True
        appt.save(update_fields=['reminder_24h_sent'])

    reminder_2h_start = now + timedelta(hours=1, minutes=45)
    reminder_2h_end = now + timedelta(hours=2, minutes=15)
    upcoming_2h = Appointment.objects.filter(
        status__in=('pending', 'confirmed'),
        reminder_2h_sent=False,
        appointment_date=reminder_2h_start.date(),
        start_time__range=(reminder_2h_start.time(), reminder_2h_end.time()),
    ).select_related('service', 'stylist', 'user')

    for appt in upcoming_2h:
        time_str = appt.start_time.strftime('%I:%M %p')
        msg = (
            f'Your {appt.service.name} at {salon_name} is in about 2 hours ({time_str}). '
            f'We look forward to seeing you! Ref: {appt.reference}'
        )
        phone = appt.client_phone
        if phone:
            send_sms(phone, msg, appointment=appt, sms_type='reminder_2h')
        appt.reminder_2h_sent = True
        appt.save(update_fields=['reminder_2h_sent'])

    return f'Sent {upcoming_24h.count()} 24h reminders, {upcoming_2h.count()} 2h reminders'


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def send_reengagement_sms(self):
    from apps.bookings.models import Appointment
    from .sms import send_sms

    salon_name = settings.SALON_NAME
    whatsapp = settings.WHATSAPP_NUMBER
    reengagement_days = settings.REENGAGEMENT_DAYS
    today = timezone.localdate()

    completed = Appointment.objects.filter(
        status='completed',
        reengagement_sent=False,
    ).select_related('service', 'user')

    sent = 0
    for appt in completed:
        category = appt.service.reengagement_category or 'default'
        days = reengagement_days.get(category, reengagement_days['default'])
        trigger_date = appt.appointment_date + timedelta(days=days)

        if trigger_date != today:
            continue

        phone = appt.client_phone
        if not phone:
            continue

        client_first = appt.client_name.split()[0] if appt.client_name else 'there'
        messages_by_category = {
            'haircut': (
                f"Hi {client_first}! It's been {days} days since your last cut at {salon_name}. "
                f"Time to keep that fresh look! Book now via WhatsApp: {whatsapp} 💈"
            ),
            'beard': (
                f"Hey {client_first}, your beard is probably missing us! 😄 "
                f"It's been {days} days – book your next trim at {salon_name}: {whatsapp}"
            ),
            'nails': (
                f"Hi {client_first}! Your nails are due for some love 💅 "
                f"It's been {days} days. Book your next nail session at {salon_name}: {whatsapp}"
            ),
            'default': (
                f"Hi {client_first}, we miss you at {salon_name}! "
                f"It's been a while – book your next appointment: {whatsapp}"
            ),
        }
        msg = messages_by_category.get(category, messages_by_category['default'])
        send_sms(phone, msg, appointment=appt, sms_type='reengagement')
        appt.reengagement_sent = True
        appt.save(update_fields=['reengagement_sent'])
        sent += 1

    return f'Sent {sent} re-engagement SMS messages'


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def send_cancellation_notification(self, appointment_id):
    from apps.bookings.models import Appointment
    from .sms import send_sms
    from .email import send_email

    try:
        appt = Appointment.objects.select_related('service', 'stylist', 'user').get(pk=appointment_id)
    except Appointment.DoesNotExist:
        return

    salon_name = settings.SALON_NAME
    phone = settings.SALON_PHONE
    msg = (
        f'Your {appt.service.name} appointment (Ref: {appt.reference}) at {salon_name} '
        f'has been cancelled. To rebook, WhatsApp us: {settings.WHATSAPP_NUMBER}'
    )

    client_phone = appt.client_phone
    if client_phone:
        send_sms(client_phone, msg, appointment=appt, sms_type='cancellation')

    client_email = appt.client_email
    if client_email:
        send_email(
            recipient=client_email,
            subject=f'Appointment Cancelled – {appt.reference} | {salon_name}',
            template_name='appointment_cancellation',
            context={'appointment': appt, 'salon_name': salon_name},
            appointment=appt,
            email_type='cancellation',
        )


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def send_birthday_promotions(self):
    from apps.accounts.models import User
    from .sms import send_sms

    today = timezone.localdate()
    salon_name = settings.SALON_NAME
    whatsapp = settings.WHATSAPP_NUMBER

    birthday_users = User.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
        sms_notifications=True,
        is_active=True,
        phone_number__gt='',
    )

    for user in birthday_users:
        msg = (
            f'Happy Birthday {user.first_name}! 🎂🎉 '
            f'Celebrate with a special treat at {salon_name}. '
            f'Show this message for a birthday discount. Book: {whatsapp}'
        )
        send_sms(user.phone_number, msg, sms_type='birthday')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, user_id, token):
    from apps.accounts.models import User
    from .email import send_email
    from django.urls import reverse

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    verify_url = f"https://{settings.ALLOWED_HOSTS[0] if not settings.DEBUG else 'localhost:8000'}{reverse('accounts:verify_email', kwargs={'token': token})}"

    send_email(
        recipient=user.email,
        subject=f'Verify your email – {settings.SALON_NAME}',
        template_name='verify_email',
        context={'user': user, 'verify_url': verify_url, 'salon_name': settings.SALON_NAME},
        email_type='verification',
    )


@shared_task(bind=True, max_retries=2)
def send_campaign_sms(self, campaign_id):
    from .models import SMSCampaign
    from apps.accounts.models import User
    from .sms import send_sms

    try:
        campaign = SMSCampaign.objects.get(pk=campaign_id, status='scheduled')
    except SMSCampaign.DoesNotExist:
        return

    campaign.status = 'sending'
    campaign.save(update_fields=['status'])

    users = User.objects.filter(is_active=True, phone_number__gt='')
    if campaign.target_marketing_opted_in and not campaign.target_all:
        users = users.filter(marketing_sms=True)

    sent = 0
    for user in users:
        send_sms(user.phone_number, campaign.message, sms_type='campaign')
        sent += 1

    campaign.status = 'sent'
    campaign.sent_count = sent
    campaign.save(update_fields=['status', 'sent_count'])
    return f'Campaign {campaign_id} sent to {sent} recipients'
