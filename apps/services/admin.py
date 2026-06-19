from django.contrib import admin
from .models import ServiceCategory, Service, Promotion


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category_type', 'is_active')


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration_minutes', 'is_active', 'is_featured', 'order')
    list_editable = ('is_active', 'is_featured', 'order')
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('category', 'name', 'slug', 'description', 'short_description')}),
        ('Pricing & Duration', {'fields': ('price', 'price_max', 'duration_minutes')}),
        ('Media', {'fields': ('image',)}),
        ('Settings', {'fields': ('is_active', 'is_featured', 'order', 'reengagement_category')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


admin.site.register(Service, ServiceAdmin)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active')
    list_editable = ('is_active',)
    filter_horizontal = ('services',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_active', 'discount_type')
    date_hierarchy = 'start_date'
