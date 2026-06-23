import json

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.core.validators import MaxValueValidator, MinValueValidator
from cart.models import Cart, CartItem
from cart.tests.factories import CartFactory, CartItemFactory, UserFactory
from cart.views import (
    AddToCartView,
    CartDetailView,
    RemoveFromCartView,
    UpdateCartItemQuantityView,
    _cart_totals,
    _parse_positive_int,
    get_active_cart,
)
from product.tests.factories import ProductVariantFactory

pytestmark = pytest.mark.django_db


def attach_session(request):
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    return request


def attach_messages(request):
    setattr(request, "_messages", FallbackStorage(request))
    return request


def build_request(method="get", path="/cart/", data=None, user=None, json=True):
    rf = RequestFactory()

    headers = {}
    if json:
        headers["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        headers["HTTP_ACCEPT"] = "application/json"

    if method.lower() == "post":
        request = rf.post(path, data=data or {}, **headers)
    else:
        request = rf.get(path, data=data or {}, **headers)

    request.user = user or AnonymousUser()
    attach_session(request)
    attach_messages(request)
    return request


def response_json(response):
    return json.loads(response.content.decode("utf-8"))


def test_parse_positive_int_defaults_for_invalid_value():
    assert _parse_positive_int("bad", default=3) == 3
    assert _parse_positive_int(None, default=2) == 2


def test_parse_positive_int_clamps_minimum_and_maximum():
    assert _parse_positive_int("0", minimum=1) == 1
    assert _parse_positive_int("100", maximum=20) == 20


def test_cart_totals_for_none_cart():
    totals = _cart_totals(None)

    assert totals == {
        "items_count": 0,
        "subtotal_toman": 0,
        "tax_toman": 0,
        "final_toman": 0,
        "is_empty": True,
    }


def test_cart_totals_for_cart_with_items():
    cart = CartFactory()
    variant_1 = ProductVariantFactory(price_toman=100_000)
    variant_2 = ProductVariantFactory(price_toman=200_000)

    CartItemFactory(cart=cart, variant=variant_1, quantity=2)
    CartItemFactory(cart=cart, variant=variant_2, quantity=1)

    totals = _cart_totals(cart)

    assert totals["items_count"] == 3
    assert totals["subtotal_toman"] == 400_000
    assert totals["tax_toman"] == 40_000
    assert totals["final_toman"] == 440_000
    assert totals["is_empty"] is False


def test_get_active_cart_anonymous_without_create_returns_none():
    request = build_request(user=AnonymousUser())

    assert get_active_cart(request, create=False) is None


def test_get_active_cart_anonymous_with_create_creates_cart_and_stores_cart_id_in_session():
    request = build_request(user=AnonymousUser())

    cart = get_active_cart(request, create=True)

    assert cart.pk is not None
    assert cart.user is None
    assert cart.status == Cart.Status.ACTIVE
    assert request.session["anonymous_cart_id"] == cart.pk


def test_get_active_cart_authenticated_with_create_creates_user_cart():
    user = UserFactory()
    request = build_request(user=user)

    cart = get_active_cart(request, create=True)

    assert cart.user == user
    assert cart.session_key == ""
    assert cart.status == Cart.Status.ACTIVE


def test_get_active_cart_authenticated_reuses_existing_user_cart():
    user = UserFactory()
    existing_cart = CartFactory(user=user, session_key="", status=Cart.Status.ACTIVE)

    request = build_request(user=user)

    cart = get_active_cart(request, create=True)

    assert cart == existing_cart
    assert Cart.objects.filter(user=user, status=Cart.Status.ACTIVE).count() == 1


def test_get_active_cart_assigns_anonymous_cart_to_authenticated_user():
    user = UserFactory()
    anonymous_cart = CartFactory(user=None, session_key="abc", status=Cart.Status.ACTIVE)

    request = build_request(user=user)
    request.session["anonymous_cart_id"] = anonymous_cart.pk
    request.session.save()

    cart = get_active_cart(request, create=True)

    anonymous_cart.refresh_from_db()

    assert cart.pk == anonymous_cart.pk
    assert cart.user == user
    assert cart.session_key == ""
    assert "anonymous_cart_id" not in request.session


def test_get_active_cart_merges_anonymous_cart_into_existing_user_cart():
    user = UserFactory()

    variant_1 = ProductVariantFactory(price_toman=100_000)
    variant_2 = ProductVariantFactory(price_toman=200_000)

    user_cart = CartFactory(user=user, session_key="", status=Cart.Status.ACTIVE)
    anonymous_cart = CartFactory(user=None, session_key="anon-session", status=Cart.Status.ACTIVE)

    user_item = CartItemFactory(cart=user_cart, variant=variant_1, quantity=15)
    CartItemFactory(cart=anonymous_cart, variant=variant_1, quantity=10)
    CartItemFactory(cart=anonymous_cart, variant=variant_2, quantity=2)

    request = build_request(user=user)
    request.session["anonymous_cart_id"] = anonymous_cart.pk
    request.session.save()

    cart = get_active_cart(request, create=True)

    user_item.refresh_from_db()
    anonymous_cart.refresh_from_db()

    assert cart == user_cart

    # Quantity is clamped to MAX_CART_ITEM_QUANTITY = 20.
    assert user_item.quantity == 20

    assert CartItem.objects.get(cart=user_cart, variant=variant_2).quantity == 2
    assert anonymous_cart.status == Cart.Status.ABANDONED
    assert anonymous_cart.session_key == ""
    assert "anonymous_cart_id" not in request.session


def test_cart_detail_context_for_empty_cart():
    request = build_request(method="get", json=False)

    view = CartDetailView()
    view.setup(request)

    context = view.get_context_data()

    assert context["cart"] is None
    assert context["cart_items"] == []
    assert context["items_count"] == 0
    assert context["subtotal_toman"] == 0
    assert context["tax_toman"] == 0
    assert context["final_toman"] == 0
    assert context["is_cart_empty"] is True
    assert context["tax_percent"] == 10


def test_cart_detail_context_with_items():
    cart = CartFactory(user=None, session_key="test-session", status=Cart.Status.ACTIVE)
    variant = ProductVariantFactory(price_toman=100_000)
    CartItemFactory(cart=cart, variant=variant, quantity=2)

    request = build_request(method="get", json=False)
    request.session["anonymous_cart_id"] = cart.pk
    request.session.save()

    view = CartDetailView()
    view.setup(request)

    context = view.get_context_data()

    assert context["cart"] == cart
    assert len(context["cart_items"]) == 1
    assert context["items_count"] == 2
    assert context["subtotal_toman"] == 200_000
    assert context["tax_toman"] == 20_000
    assert context["final_toman"] == 220_000
    assert context["is_cart_empty"] is False


def test_add_to_cart_json_creates_cart_and_item():
    variant = ProductVariantFactory(price_toman=100_000, stock_quantity=10)

    request = build_request(
        method="post",
        data={
            "quantity": "2",
        },
    )

    response = AddToCartView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    item = CartItem.objects.get(variant=variant)

    assert response.status_code == 200
    assert item.quantity == 2
    assert payload["items_count"] == 2
    assert payload["subtotal_toman"] == 200_000
    assert payload["tax_toman"] == 20_000
    assert payload["final_toman"] == 220_000
    assert payload["item"]["id"] == item.pk
    assert payload["item"]["quantity"] == 2
    assert payload["item"]["line_total_toman"] == 200_000


def test_add_to_cart_json_increments_existing_item_and_clamps_to_max_quantity():
    variant = ProductVariantFactory(price_toman=100_000, stock_quantity=50)

    request = build_request(method="post", data={"quantity": "18"})
    AddToCartView.as_view()(request, variant_id=variant.pk)

    request = build_request(method="post", data={"quantity": "10"})
    request.session["anonymous_cart_id"] = Cart.objects.get().pk
    request.session.save()

    response = AddToCartView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    item = CartItem.objects.get(variant=variant)

    assert response.status_code == 200
    assert item.quantity == 20
    assert payload["item"]["quantity"] == 20


def test_add_to_cart_json_rejects_out_of_stock_variant():
    variant = ProductVariantFactory(stock_quantity=0)

    request = build_request(method="post", data={"quantity": "1"})

    response = AddToCartView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    assert response.status_code == 400
    assert payload["detail"] == "This product variant is not available."
    assert CartItem.objects.count() == 0


def test_update_cart_item_quantity_sets_exact_quantity():
    variant = ProductVariantFactory(price_toman=100_000, stock_quantity=10)
    cart = CartFactory()
    item = CartItemFactory(cart=cart, variant=variant, quantity=1)

    request = build_request(method="post", data={"quantity": "4"})
    request.session["anonymous_cart_id"] = cart.pk
    request.session.save()

    response = UpdateCartItemQuantityView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    item.refresh_from_db()

    assert response.status_code == 200
    assert item.quantity == 4
    assert payload["item"]["quantity"] == 4
    assert payload["item"]["line_total_toman"] == 400_000


def test_update_cart_item_quantity_with_delta():
    variant = ProductVariantFactory(price_toman=100_000, stock_quantity=10)
    cart = CartFactory()
    item = CartItemFactory(cart=cart, variant=variant, quantity=3)

    request = build_request(method="post", data={"delta": "2"})
    request.session["anonymous_cart_id"] = cart.pk
    request.session.save()

    response = UpdateCartItemQuantityView.as_view()(request, variant_id=variant.pk)

    item.refresh_from_db()

    assert response.status_code == 200
    assert item.quantity == 5


def test_update_cart_item_quantity_deletes_item_when_quantity_zero():
    variant = ProductVariantFactory(price_toman=100_000, stock_quantity=10)
    cart = CartFactory()
    CartItemFactory(cart=cart, variant=variant, quantity=1)

    request = build_request(method="post", data={"quantity": "0"})
    request.session["anonymous_cart_id"] = cart.pk
    request.session.save()

    response = UpdateCartItemQuantityView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    assert response.status_code == 200
    assert CartItem.objects.filter(cart=cart, variant=variant).exists() is False
    assert payload["item"]["removed"] is True
    assert payload["is_empty"] is True


def test_update_cart_item_quantity_returns_400_without_valid_action():
    variant = ProductVariantFactory(stock_quantity=10)

    request = build_request(method="post", data={})

    response = UpdateCartItemQuantityView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    assert response.status_code == 400
    assert payload["detail"] == "quantity, delta, or action is required."


def test_update_cart_item_quantity_creates_item_when_missing_and_action_increase():
    variant = ProductVariantFactory(price_toman=100_000, stock_quantity=10)
    cart = CartFactory()

    request = build_request(method="post", data={"action": "increase"})
    request.session["anonymous_cart_id"] = cart.pk
    request.session.save()

    response = UpdateCartItemQuantityView.as_view()(request, variant_id=variant.pk)

    item = CartItem.objects.get(cart=cart, variant=variant)

    assert response.status_code == 200
    assert item.quantity == 1


def test_remove_from_cart_json_removes_item():
    variant = ProductVariantFactory(price_toman=100_000, stock_quantity=10)
    cart = CartFactory()
    CartItemFactory(cart=cart, variant=variant, quantity=2)

    request = build_request(method="post")
    request.session["anonymous_cart_id"] = cart.pk
    request.session.save()

    response = RemoveFromCartView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    assert response.status_code == 200
    assert CartItem.objects.filter(cart=cart, variant=variant).exists() is False
    assert payload["item"]["removed"] is True
    assert payload["items_count"] == 0
    assert payload["is_empty"] is True


def test_remove_from_cart_json_when_no_cart_exists():
    variant = ProductVariantFactory()

    request = build_request(method="post")

    response = RemoveFromCartView.as_view()(request, variant_id=variant.pk)
    payload = response_json(response)

    assert response.status_code == 200
    assert payload["item"]["removed"] is True
    assert payload["items_count"] == 0
    assert payload["is_empty"] is True