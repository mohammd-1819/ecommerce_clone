import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from core.models import TimeStampedModel
from accounts.models import UserAddress
from cart.tests.factories import CartFactory, UserFactory
from order.models import CheckoutSession, Coupon, Order, OrderItem, PaymentMethod
from product.tests.factories import ProductFactory, ProductVariantFactory
from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class UserAddressFactory(DjangoModelFactory):
    class Meta:
        model = UserAddress

    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"آدرس {n}")
    full_name = "علی رضایی"
    phone_number = "09123456789"
    zip_code = "1234567890"
    province = "تهران"
    city = "تهران"
    postal_address = "خیابان تست، پلاک ۱"
    plaque_number = "1"
    unit = "2"


class PaymentMethodFactory(DjangoModelFactory):
    class Meta:
        model = PaymentMethod

    code = factory.Sequence(lambda n: f"payment-{n}")
    title = factory.Sequence(lambda n: f"روش پرداخت {n}")
    description = ""
    is_online = True
    gateway_name = ""
    is_active = True


class CouponFactory(DjangoModelFactory):
    class Meta:
        model = Coupon

    code = factory.Sequence(lambda n: f"COUPON{n}")
    discount_type = Coupon.DiscountType.FIXED
    value = 50_000
    max_discount_toman = None
    min_order_amount_toman = 0
    starts_at = None
    expires_at = None
    usage_limit = None
    used_count = 0
    is_active = True


class CheckoutSessionFactory(DjangoModelFactory):
    class Meta:
        model = CheckoutSession

    user = None
    session_key = factory.Sequence(lambda n: f"checkout-session-{n}")
    cart = factory.SubFactory(CartFactory)
    selected_address = None
    payment_method = None
    coupon = None
    note = ""
    status = CheckoutSession.Status.ACTIVE
    expires_at = None


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    code = factory.Sequence(lambda n: f"ORD-{n:06d}")
    user = factory.SubFactory(UserFactory)
    checkout_session = None
    cart = factory.SubFactory(CartFactory)
    address = factory.SubFactory(UserAddressFactory)

    recipient_full_name = "علی رضایی"
    recipient_phone = "09123456789"
    province = "تهران"
    city = "تهران"
    postal_address = "خیابان تست، پلاک ۱"
    postal_code = "1234567890"

    payment_method = factory.SubFactory(PaymentMethodFactory)
    coupon = None
    shipping_method_title = "روش امن"
    payment_tracking_code = ""

    subtotal_toman = 500_000
    discount_toman = 0
    tax_toman = 50_000
    shipping_price_toman = 0
    total_toman = 550_000

    status = Order.Status.PENDING_PAYMENT
    payment_status = Order.PaymentStatus.UNPAID

    customer_note = ""
    admin_note = ""

    paid_at = None
    shipped_at = None
    delivered_at = None


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    variant = factory.SubFactory(ProductVariantFactory)

    product_title = factory.LazyAttribute(lambda obj: obj.product.title)
    variant_summary = "۲۵۰ گرم"
    unit_price_toman = 250_000
    quantity = 2
    line_total_toman = 500_000