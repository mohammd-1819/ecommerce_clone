from django.core.cache import cache
from django.db.models import Count, Q

from .models import ProductCategory


ACTIVE_PRODUCT_CATEGORIES_CACHE_KEY = "products:active_categories:v1"
SEARCH_MODAL_CATEGORIES_CACHE_KEY = "products:search_modal_categories:v1"

ACTIVE_PRODUCT_CATEGORIES_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours
SEARCH_MODAL_CATEGORIES_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours


def _load_active_product_categories():
    """
    Used in product list sidebar/filter.

    Returns only active categories.
    """
    return list(
        ProductCategory.objects.filter(is_active=True)
        .order_by("title")
        .values("id", "title", "slug")
    )


def get_cached_active_product_categories():
    return cache.get_or_set(
        ACTIVE_PRODUCT_CATEGORIES_CACHE_KEY,
        _load_active_product_categories,
        timeout=ACTIVE_PRODUCT_CATEGORIES_CACHE_TIMEOUT,
    )


def clear_active_product_categories_cache():
    cache.delete(ACTIVE_PRODUCT_CATEGORIES_CACHE_KEY)


def _load_search_modal_categories():
    """
    Used in header search modal.

    Returns active categories that have at least one active product
    with at least one active variant and active weight option.
    """
    return list(
        ProductCategory.objects.filter(is_active=True)
        .annotate(
            active_product_count=Count(
                "products",
                filter=Q(
                    products__is_active=True,
                    products__variants__is_active=True,
                    products__variants__weight__is_active=True,
                ),
                distinct=True,
            )
        )
        .filter(active_product_count__gt=0)
        .order_by("title")
        .values("id", "title", "slug", "active_product_count")
    )


def get_cached_search_modal_categories():
    return cache.get_or_set(
        SEARCH_MODAL_CATEGORIES_CACHE_KEY,
        _load_search_modal_categories,
        timeout=SEARCH_MODAL_CATEGORIES_CACHE_TIMEOUT,
    )


def clear_search_modal_categories_cache():
    cache.delete(SEARCH_MODAL_CATEGORIES_CACHE_KEY)


def clear_all_product_category_caches():
    """
    Clears every category-related cache.
    """
    clear_active_product_categories_cache()
    clear_search_modal_categories_cache()