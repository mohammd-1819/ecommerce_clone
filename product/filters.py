import django_filters

from .models import Product, ProductCategory


class ProductFilter(django_filters.FilterSet):
    SORT_CHOICES = (
        ("newest", "جدیدترین"),
        ("price_asc", "ارزان‌ترین"),
        ("price_desc", "گران‌ترین"),
        ("best_selling", "پرفروش‌ترین"),
    )

    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category__slug",
        to_field_name="slug",
        queryset=ProductCategory.objects.filter(is_active=True),
    )

    available = django_filters.CharFilter(
        method="filter_available",
    )

    price_min = django_filters.NumberFilter(
        method="filter_price_min",
        min_value=0,
    )

    price_max = django_filters.NumberFilter(
        method="filter_price_max",
        min_value=0,
    )

    sort = django_filters.ChoiceFilter(
        choices=SORT_CHOICES,
        method="filter_sort",
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "available",
            "price_min",
            "price_max",
            "sort",
        ]

    def filter_available(self, queryset, name, value):
        if str(value).lower() in ["1", "true", "on", "yes", "available"]:
            return queryset.filter(stock_status=Product.StockStatus.AVAILABLE)

        return queryset

    def filter_price_min(self, queryset, name, value):
        if value is not None:
            return queryset.filter(list_price_toman__gte=value)

        return queryset

    def filter_price_max(self, queryset, name, value):
        if value is not None:
            return queryset.filter(list_price_toman__lte=value)

        return queryset

    def filter_sort(self, queryset, name, value):
        if value == "price_asc":
            return queryset.order_by("list_price_toman", "-created_at")

        if value == "price_desc":
            return queryset.order_by("-list_price_toman", "-created_at")

        if value == "best_selling":
            return queryset.order_by("-order_counter", "-created_at")

        return queryset.order_by("-created_at")