from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'service', 'rating', 'is_approved', 'is_featured', 'created_at')
    list_editable = ('is_approved', 'is_featured')
    list_filter = ('is_approved', 'is_featured', 'rating')
    search_fields = ('client_name', 'body')
    readonly_fields = ('created_at',)
    actions = ['approve_selected']

    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} testimonial(s) approved.')
    approve_selected.short_description = 'Approve selected testimonials'
