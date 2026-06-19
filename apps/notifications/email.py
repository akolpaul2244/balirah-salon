import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_email(recipient, subject, template_name, context, appointment=None, email_type=''):
    from .models import EmailLog

    log = EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        email_type=email_type,
        appointment=appointment,
    )
    try:
        html_content = render_to_string(f'notifications/emails/{template_name}.html', context)
        text_content = render_to_string(f'notifications/emails/{template_name}.txt', context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        log.status = 'sent'
        log.sent_at = timezone.now()
    except Exception as e:
        logger.error(f'Email send failed to {recipient}: {e}')
        log.status = 'failed'
        log.error_message = str(e)
    finally:
        log.save(update_fields=['status', 'sent_at', 'error_message'])
