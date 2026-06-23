import pytest
from django.db import IntegrityError
from django.core.validators import MaxValueValidator, MinValueValidator
from cart.models import Cart, CartItem
from cart.tests.factories import CartFactory, CartItemFactory, UserFactory
from product.tests.factories import ProductVariantFactory

pytestmark = pytest.mark.django_db


def test_cart_items_count_sums_item_quantities():
    cart = CartFactory()

    CartItemFactory(cart=cart, quantity=2)
    CartItemFactory(cart=cart, quantity=3)

    assert cart.items_count == 5


def test_cart_subtotal_toman_sums_line_totals():
    cart = CartFactory()

    variant_1 = ProductVariantFactory(price_toman=100_000)
    variant_2 = ProductVariantFactory(price_toman=250_000)

    CartItemFactory(cart=cart, variant=variant_1, quantity=2)
    CartItemFactory(cart=cart, variant=variant_2, quantity=3)

    assert cart.subtotal_toman == 950_000


def test_cart_item_unit_price_uses_variant_final_price():
    variant = ProductVariantFactory(price_toman=120_000)
    item = CartItemFactory(variant=variant, quantity=2)

    assert item.unit_price_toman == 120_000


def test_cart_item_line_total_toman():
    variant = ProductVariantFactory(price_toman=120_000)
    item = CartItemFactory(variant=variant, quantity=3)

    assert item.line_total_toman == 360_000


def test_cart_has_only_one_active_cart_per_user():
    user = UserFactory()

    CartFactory(user=user, session_key="", status=Cart.Status.ACTIVE)

    with pytest.raises(IntegrityError):
        CartFactory(user=user, session_key="", status=Cart.Status.ACTIVE)


def test_cart_allows_multiple_non_active_carts_for_same_user():
    user = UserFactory()

    CartFactory(user=user, session_key="", status=Cart.Status.ORDERED)
    CartFactory(user=user, session_key="", status=Cart.Status.ABANDONED)

    assert Cart.objects.filter(user=user).count() == 2


def test_cart_has_only_one_active_cart_per_session_key():
    CartFactory(user=None, session_key="same-session", status=Cart.Status.ACTIVE)

    with pytest.raises(IntegrityError):
        CartFactory(user=None, session_key="same-session", status=Cart.Status.ACTIVE)


def test_cart_allows_empty_session_key_for_multiple_anonymous_active_carts():
    CartFactory(user=None, session_key="", status=Cart.Status.ACTIVE)
    CartFactory(user=None, session_key="", status=Cart.Status.ACTIVE)

    assert Cart.objects.filter(user=None, session_key="").count() == 2


def test_cart_item_variant_is_unique_per_cart():
    cart = CartFactory()
    variant = ProductVariantFactory()

    CartItemFactory(cart=cart, variant=variant)

    with pytest.raises(IntegrityError):
        CartItemFactory(cart=cart, variant=variant)