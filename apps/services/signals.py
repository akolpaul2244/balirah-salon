from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Service, ServiceCategory
from .constants import SERVICE_LIST_CACHE_KEY, PRICING_CACHE_KEY


@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
@receiver(post_save, sender=ServiceCategory)
@receiver(post_delete, sender=ServiceCategory)
def invalidate_service_caches(sender, **kwargs):
    cache.delete(SERVICE_LIST_CACHE_KEY)
    cache.delete(PRICING_CACHE_KEY)