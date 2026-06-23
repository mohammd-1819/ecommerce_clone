import json
from unittest.mock import Mock, patch

import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from cart.tests.factories import CartFactory, CartItemFactory, UserFactory
from order.models import Order
from order.tests.factories import (
    CheckoutSessionFactory,
    CouponFactory,
    OrderFactory,
    OrderItemFactory,
    PaymentMethodFactory,
    UserAddressFactory,
)
from order.views import (
    CheckoutDetailView,
    CouponApplyView,
    UserOrderDetailView,
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


def build_request(method="get", path="/checkout/", data=None, user=None, json_request=False):
    rf = RequestFactory()

    headers = {}
    if json_request:
        headers["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        headers["HTTP_ACCEPT"] = "application/json"

    if method.lower() == "post":
        request = rf.post(path, data=data or {}, **headers)
    else:
        request = rf.get(path, data=data or {}, **headers)

    request.user = user or UserFactory()
    attach_session(request)
    attach_messages(request)
    return request


def response_json(response):
    return json.loads(response.content.decode("utf-8"))


def test_checkout_detail_dispatch_redirects_when_cart_is_not_checkout_ready():
    user = UserFactory()
    request = build_request(user=user)

    with (
        patch("order.views.get_active_cart_for_request", return_value=None),
        patch("order.views.cart_is_checkout_ready", return_value=False),
    ):
        response = CheckoutDetailView.as_view()(request)

    assert response.status_code == 302
    assert response.url == reverse("cart:cart-detail")


def test_checkout_detail_dispatch_sets_cart_and_checkout_session_when_ready():
    user = UserFactory()
    cart = CartFactory(user=user)
    checkout_session = CheckoutSessionFactory(user=user, cart=cart)

    request = build_request(user=user)

    with (
        patch("order.views.get_active_cart_for_request", return_value=cart),
        patch("order.views.cart_is_checkout_ready", return_value=True),
        patch(
            "order.views.get_or_create_active_checkout_session",
            return_value=checkout_session,
        ),
        patch.object(
            CheckoutDetailView,
            "get",
            return_value=Mock(status_code=200),
        ),
    ):
        response = CheckoutDetailView.as_view()(request)

    assert response.status_code == 200


def test_checkout_detail_get_form_kwargs_includes_user_and_checkout_session():
    user = UserFactory()
    cart = CartFactory(user=user)
    checkout_session = CheckoutSessionFactory(user=user, cart=cart)

    request = build_request(user=user)

    view = CheckoutDetailView()
    view.setup(request)
    view.cart = cart
    view.checkout_session = checkout_session

    kwargs = view.get_form_kwargs()

    assert kwargs["user"] == user
    assert kwargs["checkout_session"] == checkout_session


def test_checkout_detail_get_initial_uses_selected_address_and_payment_method():
    user = UserFactory()
    address = UserAddressFactory(user=user)
    payment_method = PaymentMethodFactory(code="online")

    cart = CartFactory(user=user)
    checkout_session = CheckoutSessionFactory(
        user=user,
        cart=cart,
        selected_address=address,
        payment_method=payment_method,
        note="لطفاً سریع ارسال شود.",
    )

    request = build_request(user=user)

    view = CheckoutDetailView()
    view.setup(request)
    view.cart = cart
    view.checkout_session = checkout_session

    initial = view.get_initial()

    assert initial["shipping_address"] == address.pk
    assert initial["payment_method"] == "online"
    assert initial["shipping_method"] == "post"
    assert initial["order_note"] == "لطفاً سریع ارسال شود."


def test_checkout_detail_get_initial_uses_first_address_and_first_active_payment_method():
    user = UserFactory()
    older_address = UserAddressFactory(user=user)
    newer_address = UserAddressFactory(user=user)
    inactive_payment_method = PaymentMethodFactory(code="inactive", is_active=False)
    active_payment_method = PaymentMethodFactory(code="active", is_active=True)

    cart = CartFactory(user=user)
    checkout_session = CheckoutSessionFactory(
        user=user,
        cart=cart,
        selected_address=None,
        payment_method=None,
        note="",
    )

    request = build_request(user=user)

    view = CheckoutDetailView()
    view.setup(request)
    view.cart = cart
    view.checkout_session = checkout_session

    initial = view.get_initial()

    assert initial["shipping_address"] == newer_address.pk
    assert initial["payment_method"] == active_payment_method.code
    assert initial["shipping_method"] == "post"
    assert initial["order_note"] == ""


def test_checkout_detail_context_contains_cart_items_addresses_payment_methods_summary_and_coupon_form():
    user = UserFactory()
    cart = CartFactory(user=user)
    variant = ProductVariantFactory(price_toman=100_000)
    CartItemFactory(cart=cart, variant=variant, quantity=2)

    address = UserAddressFactory(user=user)
    active_payment = PaymentMethodFactory(is_active=True)
    PaymentMethodFactory(is_active=False)

    coupon = CouponFactory(code="OFF")
    checkout_session = CheckoutSessionFactory(
        user=user,
        cart=cart,
        coupon=coupon,
    )

    request = build_request(user=user)

    view = CheckoutDetailView()
    view.setup(request)
    view.cart = cart
    view.checkout_session = checkout_session

    fake_summary = {
        "subtotal_toman": 200_000,
        "discount_toman": 50_000,
        "total_toman": 150_000,
    }

    with patch("order.views.build_checkout_summary", return_value=fake_summary):
        context = view.get_context_data()

    assert context["cart"] == cart
    assert list(context["cart_items"])[0].cart == cart
    assert list(context["addresses"]) == [address]
    assert list(context["payment_methods"]) == [active_payment]
    assert context["summary"] == fake_summary
    assert context["coupon_form"].initial["coupon_code"] == "OFF"


def test_checkout_detail_form_valid_saves_form_and_redirects_to_success_url():
    user = UserFactory()
    request = build_request(user=user)

    view = CheckoutDetailView()
    view.setup(request)

    form = Mock()
    form.save = Mock()

    with patch.object(
        CheckoutDetailView,
        "get_success_url",
        return_value="/checkout/payment-start/",
    ):
        response = view.form_valid(form)

    form.save.assert_called_once()
    assert response.status_code == 302
    assert response.url == "/checkout/payment-start/"


def test_coupon_apply_returns_400_when_cart_is_not_ready_json():
    user = UserFactory()
    request = build_request(
        method="post",
        data={"coupon_code": "OFF"},
        user=user,
        json_request=True,
    )

    with (
        patch("order.views.get_active_cart_for_request", return_value=None),
        patch("order.views.cart_is_checkout_ready", return_value=False),
    ):
        response = CouponApplyView.as_view()(request)

    payload = response_json(response)

    assert response.status_code == 400
    assert payload["ok"] is False
    assert payload["message"] == "سبد خرید شما خالی است."


def test_coupon_apply_removes_coupon_when_code_is_empty_json():
    user = UserFactory()
    cart = CartFactory(user=user)
    coupon = CouponFactory(code="OFF")
    checkout_session = CheckoutSessionFactory(
        user=user,
        cart=cart,
        coupon=coupon,
    )

    request = build_request(
        method="post",
        data={"coupon_code": ""},
        user=user,
        json_request=True,
    )

    fake_summary = {"total_toman": 100_000}

    with (
        patch("order.views.get_active_cart_for_request", return_value=cart),
        patch("order.views.cart_is_checkout_ready", return_value=True),
        patch(
            "order.views.get_or_create_active_checkout_session",
            return_value=checkout_session,
        ),
        patch("order.views.build_checkout_summary", return_value=fake_summary),
        patch("order.views.summary_to_json", side_effect=lambda summary: summary),
    ):
        response = CouponApplyView.as_view()(request)

    checkout_session.refresh_from_db()
    payload = response_json(response)

    assert response.status_code == 200
    assert checkout_session.coupon is None
    assert payload["ok"] is True
    assert payload["message"] == "کد تخفیف حذف شد."
    assert payload["coupon"] is None
    assert payload["summary"] == fake_summary


def test_coupon_apply_returns_error_when_coupon_validation_fails_json():
    user = UserFactory()
    cart = CartFactory(user=user)
    checkout_session = CheckoutSessionFactory(user=user, cart=cart)

    request = build_request(
        method="post",
        data={"coupon_code": "BAD"},
        user=user,
        json_request=True,
    )

    fake_summary = {"total_toman": 100_000}

    with (
        patch("order.views.get_active_cart_for_request", return_value=cart),
        patch("order.views.cart_is_checkout_ready", return_value=True),
        patch(
            "order.views.get_or_create_active_checkout_session",
            return_value=checkout_session,
        ),
        patch(
            "order.views.validate_coupon_for_cart",
            return_value=(None, "کد تخفیف قابل استفاده نیست."),
        ),
        patch("order.views.build_checkout_summary", return_value=fake_summary),
        patch("order.views.summary_to_json", side_effect=lambda summary: summary),
    ):
        response = CouponApplyView.as_view()(request)

    payload = response_json(response)

    assert response.status_code == 400
    assert payload["ok"] is False
    assert payload["message"] == "کد تخفیف قابل استفاده نیست."
    assert payload["summary"] == fake_summary


def test_coupon_apply_applies_valid_coupon_json():
    user = UserFactory()
    cart = CartFactory(user=user)
    checkout_session = CheckoutSessionFactory(user=user, cart=cart)
    coupon = CouponFactory(code="OFF50", value=50_000)

    request = build_request(
        method="post",
        data={"coupon_code": "OFF50"},
        user=user,
        json_request=True,
    )

    fake_summary = {"total_toman": 150_000}

    with (
        patch("order.views.get_active_cart_for_request", return_value=cart),
        patch("order.views.cart_is_checkout_ready", return_value=True),
        patch(
            "order.views.get_or_create_active_checkout_session",
            return_value=checkout_session,
        ),
        patch(
            "order.views.validate_coupon_for_cart",
            return_value=(coupon, None),
        ),
        patch("order.views.build_checkout_summary", return_value=fake_summary),
        patch("order.views.summary_to_json", side_effect=lambda summary: summary),
    ):
        response = CouponApplyView.as_view()(request)

    checkout_session.refresh_from_db()
    payload = response_json(response)

    assert response.status_code == 200
    assert checkout_session.coupon == coupon
    assert payload["ok"] is True
    assert payload["message"] == "کد تخفیف با موفقیت اعمال شد."
    assert payload["coupon"]["id"] == coupon.pk
    assert payload["coupon"]["code"] == "OFF50"
    assert payload["summary"] == fake_summary


def test_user_order_detail_get_queryset_limits_orders_to_current_user_and_annotates_items_count():
    user = UserFactory()
    other_user = UserFactory()

    user_order = OrderFactory(user=user)
    other_order = OrderFactory(user=other_user)

    OrderItemFactory(order=user_order, quantity=2)
    OrderItemFactory(order=user_order, quantity=3)
    OrderItemFactory(order=other_order, quantity=10)

    request = build_request(user=user)

    view = UserOrderDetailView()
    view.setup(request)

    queryset = view.get_queryset()

    assert queryset.filter(pk=user_order.pk).exists() is True
    assert queryset.filter(pk=other_order.pk).exists() is False

    fetched_order = queryset.get(pk=user_order.pk)
    assert fetched_order.items_count == 5


def test_user_order_detail_get_object_by_order_code():
    user = UserFactory()
    order = OrderFactory(user=user, code="ORD-CODE-1")

    request = build_request(user=user)

    view = UserOrderDetailView()
    view.setup(request, order_code="ORD-CODE-1")

    assert view.get_object() == order


def test_user_order_detail_get_order_status_badge_class():
    view = UserOrderDetailView()

    order = OrderFactory(status=Order.Status.PAID)

    assert view.get_order_status_badge_class(order) == "order-status-paid"


def test_user_order_detail_get_payment_status_class():
    view = UserOrderDetailView()

    order = OrderFactory(payment_status=Order.PaymentStatus.FAILED)

    assert view.get_payment_status_class(order) == "text-danger"


def test_user_order_detail_timeline_for_cancelled_order():
    view = UserOrderDetailView()
    order = OrderFactory(status=Order.Status.CANCELLED)

    steps = view.get_timeline_steps(order)

    assert len(steps) == 2
    assert steps[0]["state_class"] == "is-complete"
    assert steps[1]["title"] == "لغو سفارش"
    assert steps[1]["state_class"] == "is-active"


def test_user_order_detail_timeline_for_refunded_order():
    view = UserOrderDetailView()
    order = OrderFactory(status=Order.Status.REFUNDED)

    steps = view.get_timeline_steps(order)

    assert len(steps) == 3
    assert steps[-1]["title"] == "بازگشت وجه"
    assert steps[-1]["state_class"] == "is-active"


def test_user_order_detail_timeline_for_preparing_order():
    view = UserOrderDetailView()
    order = OrderFactory(status=Order.Status.PREPARING)

    steps = view.get_timeline_steps(order)

    assert steps[0]["state_class"] == "is-complete"
    assert steps[1]["state_class"] == "is-complete"
    assert steps[2]["state_class"] == "is-active"
    assert steps[3]["state_class"] == ""
    assert steps[4]["state_class"] == ""


def test_user_order_detail_timeline_for_delivered_order_marks_all_complete():
    view = UserOrderDetailView()
    order = OrderFactory(status=Order.Status.DELIVERED)

    steps = view.get_timeline_steps(order)

    assert all(step["state_class"] == "is-complete" for step in steps)