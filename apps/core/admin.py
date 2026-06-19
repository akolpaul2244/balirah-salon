from django.contrib import admin
from django.utils.html import format_html
from .models import SalonSettings, OpeningHours, ContactMessage


@admin.register(SalonSettings)
class SalonSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identity', {'fields': ('salon_name', 'tagline', 'logo', 'favicon')}),
        ('About', {'fields': ('about_short', 'about_full', 'hero_image')}),
        ('Contact', {'fields': ('phone_primary', 'phone_secondary', 'email', 'address', 'whatsapp_number', 'google_maps_embed')}),
        ('Social Media', {'fields': ('instagram_url', 'facebook_url', 'tiktok_url')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'google_analytics_id')}),
        ('Legal', {'fields': ('privacy_policy', 'terms_conditions')}),
    )

    def has_add_permission(self, request):
        return not SalonSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('get_day_display', 'open_time', 'close_time', 'is_closed')
    list_editable = ('open_time', 'close_time', 'is_closed')
    ordering = ['day']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'ip_address', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'ip_address', 'created_at')
    date_hierarchy = 'created_at'
    list_editable = ('status',)

    def has_add_permission(self, request):
        return False
