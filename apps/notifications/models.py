from django.db import models
from django.conf import settings


class SMSLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]
    recipient = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    provider_response = models.JSONField(default=dict, blank=True)
    appointment = models.ForeignKey(
        'bookings.Appointment', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sms_logs'
    )
    sms_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'sms_type']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'SMS to {self.recipient} [{self.status}]'


class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    recipient = models.EmailField()
    subject = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    email_type = models.CharField(max_length=50, blank=True)
    appointment = models.ForeignKey(
        'bookings.Appointment', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='email_logs'
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Email to {self.recipient} [{self.status}]'


class SMSCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField(max_length=160)
    target_all = models.BooleanField(default=False)
    target_marketing_opted_in = models.BooleanField(default=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='sms_campaigns'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
