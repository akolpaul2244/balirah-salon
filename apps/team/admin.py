from django.contrib import admin
from .models import Stylist


@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'role', 'years_experience', 'is_active', 'order')
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
