from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .cache import (
    clear_all_product_category_caches,
    clear_search_modal_categories_cache,
)
from .models import Product, ProductCategory, ProductVariant, WeightOption


@receiver(post_save, sender=ProductCategory)
def clear_category_caches_after_category_save(sender, instance, **kwargs):
    clear_all_product_category_caches()


@receiver(post_delete, sender=ProductCategory)
def clear_category_caches_after_category_delete(sender, instance, **kwargs):
    clear_all_product_category_caches()


@receiver(post_save, sender=Product)
def clear_search_category_cache_after_product_save(sender, instance, **kwargs):
    clear_search_modal_categories_cache()


@receiver(post_delete, sender=Product)
def clear_search_category_cache_after_product_delete(sender, instance, **kwargs):
    clear_search_modal_categories_cache()


@receiver(post_save, sender=ProductVariant)
def clear_search_category_cache_after_variant_save(sender, instance, **kwargs):
    clear_search_modal_categories_cache()


@receiver(post_delete, sender=ProductVariant)
def clear_search_category_cache_after_variant_delete(sender, instance, **kwargs):
    clear_search_modal_categories_cache()


@receiver(post_save, sender=WeightOption)
def clear_search_category_cache_after_weight_save(sender, instance, **kwargs):
    clear_search_modal_categories_cache()


@receiver(post_delete, sender=WeightOption)
def clear_search_category_cache_after_weight_delete(sender, instance, **kwargs):
    clear_search_modal_categories_cache()