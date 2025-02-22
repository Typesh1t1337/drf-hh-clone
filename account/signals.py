from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model



@receiver(post_save, sender=None)
def clear_user_cache(sender, instance, **kwargs):
    user = get_user_model()
    if isinstance(instance, user):
        cache.delete(f"user_{instance.pk}")



