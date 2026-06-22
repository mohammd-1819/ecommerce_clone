from django.core.cache import cache

from .models import ProductCategory


ACTIVE_PRODUCT_CATEGORIES_CACHE_KEY = "products:active_categories:v1"
ACTIVE_PRODUCT_CATEGORIES_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours


def _load_active_product_categories():
    """
    Load active product categories from database.

    We return a list of dictionaries instead of a QuerySet because:
    - QuerySets are lazy.
    - QuerySets are not ideal cache values.
    - The template can still use category.title and category.slug.
    """
    return list(
        ProductCategory.objects.filter(is_active=True)
        .order_by("title")
        .values("id", "title", "slug")
    )


def get_cached_active_product_categories():
    """
    Return active product categories from Redis cache.
    If cache is empty, load from DB and store in cache.
    """
    return cache.get_or_set(
        ACTIVE_PRODUCT_CATEGORIES_CACHE_KEY,
        _load_active_product_categories,
        timeout=ACTIVE_PRODUCT_CATEGORIES_CACHE_TIMEOUT,
    )


def clear_active_product_categories_cache():
    """
    Clear cached active categories.
    Used when ProductCategory is saved or deleted.
    """
    cache.delete(ACTIVE_PRODUCT_CATEGORIES_CACHE_KEY)