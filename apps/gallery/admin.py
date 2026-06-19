from django.contrib import admin
from .models import GalleryCategory, GalleryImage


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'stylist', 'is_featured', 'is_before_after', 'order', 'created_at')
    list_editable = ('is_featured', 'order')
    list_filter = ('category', 'is_featured', 'is_before_after', 'stylist')
    search_fields = ('title',)
    readonly_fields = ('created_at',)
