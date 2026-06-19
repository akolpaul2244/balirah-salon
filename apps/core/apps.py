from django.contrib.admin import AdminSite
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = 'Balirah Beauty Salon Admin'
        admin.site.site_title = 'Balirah Admin'
        admin.site.index_title = 'Dashboard'
