from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .cache import clear_active_product_categories_cache
from .models import ProductCategory


@receiver(post_save, sender=ProductCategory)
def clear_categories_cache_after_save(sender, instance, **kwargs):
    clear_active_product_categories_cache()


@receiver(post_delete, sender=ProductCategory)
def clear_categories_cache_after_delete(sender, instance, **kwargs):
    clear_active_product_categories_cache()