import pytest
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from order.models import Order
from order.tests.factories import (
    CouponFactory,
    OrderFactory,
    OrderItemFactory,
    PaymentMethodFactory,
)

pytestmark = pytest.mark.django_db


def test_coupon_str_returns_code():
    coupon = CouponFactory(code="OFF50")

    assert str(coupon) == "OFF50"


def test_payment_method_str_returns_title():
    payment_method = PaymentMethodFactory(title="پرداخت آنلاین")

    assert str(payment_method) == "پرداخت آنلاین"

def test_order_str_returns_code():
    order = OrderFactory(code="ORD-TEST-1")

    assert str(order) == "ORD-TEST-1"


def test_order_mark_paid_updates_payment_status_order_status_and_paid_at():
    order = OrderFactory(
        status=Order.Status.PENDING_PAYMENT,
        payment_status=Order.PaymentStatus.UNPAID,
        paid_at=None,
    )

    order.mark_paid()
    order.refresh_from_db()

    assert order.status == Order.Status.PAID
    assert order.payment_status == Order.PaymentStatus.PAID
    assert order.paid_at is not None
    assert order.paid_at <= timezone.now()


def test_order_item_display_title_uses_snapshot_product_title():
    item = OrderItemFactory(product_title="عنوان ذخیره‌شده")

    assert item.display_title == "عنوان ذخیره‌شده"


def test_order_item_display_title_falls_back_to_product_title():
    item = OrderItemFactory(product_title="")

    assert item.display_title == item.product.title


def test_order_item_display_title_returns_deleted_product_label_without_product():
    item = OrderItemFactory(product=None, product_title="")

    assert item.display_title == "محصول حذف‌شده"


def test_order_item_display_meta_includes_variant_summary_and_quantity():
    item = OrderItemFactory(
        variant_summary="۵۰۰ گرم",
        quantity=3,
    )

    assert item.display_meta == "۵۰۰ گرم • تعداد 3"


def test_order_item_display_meta_without_variant_summary():
    item = OrderItemFactory(
        variant_summary="",
        quantity=2,
    )

    assert item.display_meta == "تعداد 2"