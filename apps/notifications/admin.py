from django.contrib import admin
from .models import SMSLog, EmailLog, SMSCampaign


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sms_type', 'status', 'appointment', 'created_at', 'sent_at')
    list_filter = ('status', 'sms_type')
    search_fields = ('recipient',)
    readonly_fields = ('recipient', 'message', 'status', 'provider_response', 'sms_type', 'created_at', 'sent_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'subject', 'email_type', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'email_type')
    search_fields = ('recipient', 'subject')
    readonly_fields = ('recipient', 'subject', 'status', 'email_type', 'error_message', 'created_at', 'sent_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False


@admin.register(SMSCampaign)
class SMSCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'sent_count', 'scheduled_at', 'created_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'message')
    readonly_fields = ('sent_count', 'created_at')
    fieldsets = (
        (None, {'fields': ('title', 'message', 'status')}),
        ('Targeting', {'fields': ('target_all', 'target_marketing_opted_in')}),
        ('Schedule', {'fields': ('scheduled_at',)}),
        ('Stats', {'fields': ('sent_count', 'created_by', 'created_at')}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        if obj.status == 'scheduled' and not change:
            from .tasks import send_campaign_sms
            if obj.scheduled_at:
                send_campaign_sms.apply_async((obj.pk,), eta=obj.scheduled_at)
            else:
                send_campaign_sms.delay(obj.pk)
