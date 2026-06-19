import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AfricasTalkingBackend:
    BASE_URL = 'https://api.africastalking.com/version1/messaging'

    def __init__(self):
        self.username = settings.AFRICAS_TALKING_USERNAME
        self.api_key = settings.AFRICAS_TALKING_API_KEY
        self.sender_id = settings.AFRICAS_TALKING_SENDER_ID

    def send(self, recipient, message):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'apiKey': self.api_key,
        }
        payload = {
            'username': self.username,
            'to': recipient,
            'message': message,
            'from': self.sender_id,
        }
        try:
            response = requests.post(self.BASE_URL, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            recipients = data.get('SMSMessageData', {}).get('Recipients', [])
            if recipients:
                status = recipients[0].get('status', 'Unknown')
                return {'success': status == 'Success', 'response': data}
            return {'success': False, 'response': data}
        except requests.RequestException as e:
            logger.error(f'SMS send failed to {recipient}: {e}')
            return {'success': False, 'error': str(e)}


class ConsoleSMSBackend:
    def send(self, recipient, message):
        logger.info(f'[CONSOLE SMS] To: {recipient}\nMessage: {message}')
        return {'success': True, 'response': 'console'}


def get_sms_backend():
    provider = getattr(settings, 'SMS_PROVIDER', 'console')
    if provider == 'africas_talking':
        return AfricasTalkingBackend()
    return ConsoleSMSBackend()


def send_sms(recipient, message, appointment=None, sms_type=''):
    from .models import SMSLog
    from django.utils import timezone

    log = SMSLog.objects.create(
        recipient=recipient,
        message=message,
        appointment=appointment,
        sms_type=sms_type,
    )
    backend = get_sms_backend()
    result = backend.send(recipient, message)
    log.status = 'sent' if result.get('success') else 'failed'
    log.provider_response = result.get('response', {})
    log.sent_at = timezone.now() if result.get('success') else None
    log.save(update_fields=['status', 'provider_response', 'sent_at'])
    return result
