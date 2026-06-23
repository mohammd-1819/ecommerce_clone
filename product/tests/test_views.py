import pytest
from django.test import RequestFactory

from product.models import Product, ProductReview
from product.views import ProductDetailView, ProductListView

from product.tests.factories import (
    ProductAttributeFactory,
    ProductCategoryFactory,
    ProductFactory,
    ProductImageFactory,
    ProductReviewFactory,
    ProductVariantFactory,
    WeightOptionFactory,
)

pytestmark = pytest.mark.django_db


def build_list_view(path="/products/", data=None):
    request = RequestFactory().get(path, data=data or {})
    view = ProductListView()
    view.setup(request)
    return view


def build_detail_view(product, path=None):
    request = RequestFactory().get(path or f"/products/{product.slug}/")
    view = ProductDetailView()
    view.setup(request, slug=product.slug)
    view.object = view.get_queryset().get(slug=product.slug)
    return view


def test_product_list_base_queryset_returns_only_active_products_with_active_category_and_active_variant():
    active_category = ProductCategoryFactory(is_active=True)
    inactive_category = ProductCategoryFactory(is_active=False)

    visible_product = ProductFactory(
        category=active_category,
        is_active=True,
        title="Visible product",
    )
    ProductVariantFactory(
        product=visible_product,
        is_active=True,
        is_default=True,
        price_toman=100_000,
        weight=WeightOptionFactory(value_grams=250, title="۲۵۰ گرم"),
    )

    inactive_product = ProductFactory(
        category=active_category,
        is_active=False,
    )
    ProductVariantFactory(product=inactive_product, is_active=True)

    inactive_category_product = ProductFactory(
        category=inactive_category,
        is_active=True,
    )
    ProductVariantFactory(product=inactive_category_product, is_active=True)

    no_active_variant_product = ProductFactory(
        category=active_category,
        is_active=True,
    )
    ProductVariantFactory(product=no_active_variant_product, is_active=False)

    no_variant_product = ProductFactory(
        category=active_category,
        is_active=True,
    )

    view = build_list_view()
    products = list(view.get_base_queryset())

    assert products == [visible_product]
    assert inactive_product not in products
    assert inactive_category_product not in products
    assert no_active_variant_product not in products
    assert no_variant_product not in products


def test_product_list_base_queryset_annotates_default_variant_price_and_weight():
    product = ProductFactory()

    ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=False,
        price_toman=100_000,
        weight=WeightOptionFactory(value_grams=250, title="۲۵۰ گرم"),
    )

    ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=True,
        price_toman=200_000,
        weight=WeightOptionFactory(value_grams=500, title="۵۰۰ گرم"),
    )

    view = build_list_view()
    fetched_product = view.get_base_queryset().get(pk=product.pk)

    assert fetched_product.list_price_toman == 200_000
    assert fetched_product.list_weight_title == "۵۰۰ گرم"


def test_product_list_base_queryset_without_default_variant_uses_lowest_weight_variant():
    product = ProductFactory()

    ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=False,
        price_toman=300_000,
        weight=WeightOptionFactory(value_grams=500, title="۵۰۰ گرم"),
    )

    ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=False,
        price_toman=150_000,
        weight=WeightOptionFactory(value_grams=250, title="۲۵۰ گرم"),
    )

    view = build_list_view()
    fetched_product = view.get_base_queryset().get(pk=product.pk)

    assert fetched_product.list_price_toman == 150_000
    assert fetched_product.list_weight_title == "۲۵۰ گرم"


def test_product_list_base_queryset_prefetches_only_active_variants():
    product = ProductFactory()

    active_variant = ProductVariantFactory(
        product=product,
        is_active=True,
        weight=WeightOptionFactory(value_grams=250),
    )
    inactive_variant = ProductVariantFactory(
        product=product,
        is_active=False,
        weight=WeightOptionFactory(value_grams=500),
    )

    view = build_list_view()
    fetched_product = list(view.get_base_queryset())[0]

    prefetched_variants = list(fetched_product.variants.all())

    assert active_variant in prefetched_variants
    assert inactive_variant not in prefetched_variants


def test_product_list_context_contains_pagination_and_filter_metadata():
    for index in range(7):
        product = ProductFactory(slug=f"paginated-product-{index}")
        ProductVariantFactory(product=product, is_active=True)

    view = build_list_view(data={"sort": "newest"})
    view.object_list = view.get_queryset()

    context = view.get_context_data(object_list=view.object_list)

    assert context["total_count"] == 7
    assert context["page_start_index"] == 1
    assert context["page_end_index"] == 6
    assert context["current_sort"] == "newest"
    assert context["has_filter_values"] is False
    assert context["filterset"] is view.filterset
    assert "categories" in context


def test_product_list_context_detects_selected_filters():
    category = ProductCategoryFactory(slug="nuts")

    for index in range(7):
        product = ProductFactory(
            category=category,
            slug=f"nuts-product-{index}",
        )
        ProductVariantFactory(
            product=product,
            is_active=True,
            price_toman=200_000,
            stock_quantity=5,
        )

    view = build_list_view(
        data={
            "category": ["nuts"],
            "available": "1",
            "price_min": "100000",
            "price_max": "300000",
            "sort": "newest",
            "page": "2",
        }
    )
    view.object_list = view.get_queryset()

    context = view.get_context_data(object_list=view.object_list)

    assert context["selected_category_slugs"] == ["nuts"]
    assert context["available_selected"] is True
    assert context["price_min_value"] == "100000"
    assert context["price_max_value"] == "300000"
    assert context["current_sort"] == "newest"

    assert context["has_filter_values"] is True
    assert "page=" not in context["querystring"]


def test_product_detail_queryset_returns_only_active_product():
    active_product = ProductFactory(is_active=True)
    inactive_product = ProductFactory(is_active=False)

    view = ProductDetailView()
    queryset = view.get_queryset()

    assert queryset.filter(pk=active_product.pk).exists() is True
    assert queryset.filter(pk=inactive_product.pk).exists() is False


def test_product_detail_queryset_prefetches_active_variants_ordered_by_weight():
    product = ProductFactory()

    variant_500 = ProductVariantFactory(
        product=product,
        is_active=True,
        weight=WeightOptionFactory(value_grams=500),
    )
    inactive_variant = ProductVariantFactory(
        product=product,
        is_active=False,
        weight=WeightOptionFactory(value_grams=750),
    )
    variant_250 = ProductVariantFactory(
        product=product,
        is_active=True,
        weight=WeightOptionFactory(value_grams=250),
    )

    view = ProductDetailView()
    fetched_product = view.get_queryset().get(pk=product.pk)

    variants = list(fetched_product.variants.all())

    assert variants == [variant_250, variant_500]
    assert inactive_variant not in variants


def test_product_detail_queryset_prefetches_images_main_first():
    product = ProductFactory()

    normal_image = ProductImageFactory(
        product=product,
        is_main=False,
        alt_text="تصویر معمولی",
    )
    main_image = ProductImageFactory(
        product=product,
        is_main=True,
        alt_text="تصویر اصلی",
    )

    view = ProductDetailView()
    fetched_product = view.get_queryset().get(pk=product.pk)

    images = list(fetched_product.images.all())

    assert images[0] == main_image
    assert normal_image in images


def test_product_detail_queryset_prefetches_only_approved_reviews_to_attr():
    product = ProductFactory()

    approved_review = ProductReviewFactory(
        product=product,
        status=ProductReview.Status.APPROVED,
    )
    pending_review = ProductReviewFactory(
        product=product,
        status=ProductReview.Status.PENDING,
    )

    view = ProductDetailView()
    fetched_product = view.get_queryset().get(pk=product.pk)

    assert hasattr(fetched_product, "approved_reviews")

    reviews = list(fetched_product.approved_reviews)

    assert reviews == [approved_review]
    assert pending_review not in reviews


def test_product_detail_context_uses_default_variant():
    product = ProductFactory()

    ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=False,
        weight=WeightOptionFactory(value_grams=250),
    )
    default_variant = ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=True,
        weight=WeightOptionFactory(value_grams=500),
    )

    view = build_detail_view(product)
    context = view.get_context_data(object=view.object)

    assert context["default_variant"] == default_variant


def test_product_detail_context_falls_back_to_first_variant_when_no_default_exists():
    product = ProductFactory()

    first_variant = ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=False,
        weight=WeightOptionFactory(value_grams=250),
    )
    ProductVariantFactory(
        product=product,
        is_active=True,
        is_default=False,
        weight=WeightOptionFactory(value_grams=500),
    )

    view = build_detail_view(product)
    context = view.get_context_data(object=view.object)

    assert context["default_variant"] == first_variant


def test_product_detail_context_handles_product_without_variants():
    product = ProductFactory()

    view = build_detail_view(product)
    context = view.get_context_data(object=view.object)

    assert context["variants"] == []
    assert context["default_variant"] is None


def test_product_detail_context_contains_gallery_attributes_and_reviews():
    product = ProductFactory()

    ProductVariantFactory(product=product, is_active=True)

    image = ProductImageFactory(product=product)
    attribute = ProductAttributeFactory(product=product)
    approved_review = ProductReviewFactory(
        product=product,
        status=ProductReview.Status.APPROVED,
    )
    ProductReviewFactory(
        product=product,
        status=ProductReview.Status.REJECTED,
    )

    view = build_detail_view(product)
    context = view.get_context_data(object=view.object)

    assert list(context["gallery_images"]) == [image]
    assert list(context["attributes"]) == [attribute]
    assert context["reviews"] == [approved_review]
    assert context["review_count"] == 1


def test_product_detail_context_related_products_are_same_category_active_and_exclude_current_product():
    category = ProductCategoryFactory()

    product = ProductFactory(category=category)

    featured_related = ProductFactory(
        category=category,
        is_active=True,
        is_featured=True,
        slug="featured-related-product",
    )
    normal_related = ProductFactory(
        category=category,
        is_active=True,
        is_featured=False,
        slug="normal-related-product",
    )
    inactive_related = ProductFactory(
        category=category,
        is_active=False,
        slug="inactive-related-product",
    )

    other_category_product = ProductFactory(
        category=ProductCategoryFactory(),
        is_active=True,
        slug="other-category-product",
    )

    ProductVariantFactory(product=featured_related, is_active=True)
    ProductVariantFactory(product=normal_related, is_active=True)
    ProductVariantFactory(product=inactive_related, is_active=True)
    ProductVariantFactory(product=other_category_product, is_active=True)

    view = build_detail_view(product)
    context = view.get_context_data(object=view.object)

    related_products = list(context["related_products"])

    assert featured_related in related_products
    assert normal_related in related_products

    assert product not in related_products
    assert inactive_related not in related_products
    assert other_category_product not in related_products

    assert related_products[0] == featured_related