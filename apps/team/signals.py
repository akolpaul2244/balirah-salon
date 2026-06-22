from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Stylist
from .constants import TEAM_CACHE_KEY


@receiver(post_save, sender=Stylist)
@receiver(post_delete, sender=Stylist)
def invalidate_team_cache(sender, **kwargs):
    cache.delete(TEAM_CACHE_KEY)