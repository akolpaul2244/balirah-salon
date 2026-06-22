from django.contrib import admin
from django.utils.html import format_html
from .models import Stylist
from cloudinary.utils import cloudinary_url


@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'preview_thumb', 'role', 'years_experience', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('role', 'is_active', 'specializations')
    search_fields = ('first_name', 'last_name')
    prepopulated_fields = {'slug': ('first_name', 'last_name')}
    filter_horizontal = ('specializations',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'slug', 'role', 'specializations')}),
        ('Profile', {'fields': ('bio', 'years_experience', 'photo', 'instagram')}),
        ('Settings', {'fields': ('is_active', 'order')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    @admin.display(description='Photo')
    def preview_thumb(self, obj):
        if obj.photo:
            url, _ = cloudinary_url(str(obj.photo), width=60, height=70, crop='fill', gravity='face')
            return format_html('<img src="{}" style="border-radius:4px;" />', url)
        return '—'