import pytest

from product.models import ProductReview

from product.tests.factories import (
    ProductFactory,
    ProductReviewFactory,
    ProductVariantFactory,
    WeightOptionFactory,
)

pytestmark = pytest.mark.django_db


def test_product_default_variant_returns_active_default_variant():
    product = ProductFactory()

    non_default_variant = ProductVariantFactory(
        product=product,
        weight=WeightOptionFactory(value_grams=250),
        is_default=False,
        is_active=True,
    )
    default_variant = ProductVariantFactory(
        product=product,
        weight=WeightOptionFactory(value_grams=500),
        is_default=True,
        is_active=True,
    )

    assert product.default_variant == default_variant
    assert product.default_variant != non_default_variant


def test_product_default_variant_falls_back_to_first_active_variant():
    product = ProductFactory()

    inactive_default = ProductVariantFactory(
        product=product,
        weight=WeightOptionFactory(value_grams=250),
        is_default=True,
        is_active=False,
    )
    active_variant = ProductVariantFactory(
        product=product,
        weight=WeightOptionFactory(value_grams=500),
        is_default=False,
        is_active=True,
    )

    assert product.default_variant == active_variant
    assert product.default_variant != inactive_default


def test_product_default_variant_returns_none_without_active_variants():
    product = ProductFactory()

    ProductVariantFactory(
        product=product,
        is_default=True,
        is_active=False,
    )

    assert product.default_variant is None


def test_product_is_available_true_when_active_variant_has_stock():
    product = ProductFactory()

    ProductVariantFactory(
        product=product,
        is_active=True,
        stock_quantity=3,
    )

    assert product.is_available is True


def test_product_is_available_false_when_only_inactive_variant_has_stock():
    product = ProductFactory()

    ProductVariantFactory(
        product=product,
        is_active=False,
        stock_quantity=10,
    )

    assert product.is_available is False


def test_product_is_available_false_when_active_variant_has_zero_stock():
    product = ProductFactory()

    ProductVariantFactory(
        product=product,
        is_active=True,
        stock_quantity=0,
    )

    assert product.is_available is False


def test_product_variant_is_in_stock():
    variant = ProductVariantFactory(stock_quantity=1)

    assert variant.is_in_stock is True


def test_product_variant_is_not_in_stock_when_quantity_is_zero():
    variant = ProductVariantFactory(stock_quantity=0)

    assert variant.is_in_stock is False


def test_product_variant_final_price_equals_price_toman():
    variant = ProductVariantFactory(price_toman=390_000)

    assert variant.final_price_toman == 390_000


def test_product_review_full_name():
    review = ProductReviewFactory(
        first_name="سارا",
        last_name="احمدی",
        status=ProductReview.Status.APPROVED,
    )

    assert review.full_name == "سارا احمدی"


def test_product_review_full_name_strips_extra_space():
    review = ProductReviewFactory(
        first_name="سارا",
        last_name="",
    )

    assert review.full_name == "سارا"