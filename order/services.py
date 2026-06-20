from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from cart.models import Cart
from .models import CheckoutSession, Coupon


@dataclass(frozen=True)
class CheckoutSummary:
    items_count: int
    subtotal_toman: int
    discount_toman: int
    tax_toman: int
    shipping_price_toman: int
    total_toman: int
    coupon: Coupon | None = None


def format_toman(value: int) -> str:
    return f"{int(value):,} تومان"


def get_active_cart_for_request(request):
    """
    Gets the active cart that should be used for checkout.
    For this checkout flow, authenticated user cart is preferred.
    """

    qs = (
        Cart.objects.filter(status=Cart.Status.ACTIVE)
        .prefetch_related(
            "items__variant__product",
            "items__variant__weight",
        )
    )

    if request.user.is_authenticated:
        return qs.filter(user=request.user).first()

    session_key = request.session.session_key
    if not session_key:
        return None

    return qs.filter(session_key=session_key).first()


def cart_is_checkout_ready(cart) -> bool:
    if cart is None:
        return False

    return cart.items.exists()


def get_or_create_active_checkout_session(request, cart):
    """
    Keeps one active checkout session for the current active cart.
    Expired active sessions are marked expired before a new one is created.
    """

    now = timezone.now()
    ttl_minutes = getattr(settings, "CHECKOUT_SESSION_TTL_MINUTES", 60)

    CheckoutSession.objects.filter(
        cart=cart,
        status=CheckoutSession.Status.ACTIVE,
        expires_at__isnull=False,
        expires_at__lt=now,
    ).update(status=CheckoutSession.Status.EXPIRED)

    checkout_session = (
        CheckoutSession.objects.filter(
            cart=cart,
            status=CheckoutSession.Status.ACTIVE,
        )
        .order_by("-updated_at")
        .first()
    )

    if checkout_session:
        changed_fields = []

        if request.user.is_authenticated and checkout_session.user_id != request.user.id:
            checkout_session.user = request.user
            changed_fields.append("user")

        if not checkout_session.session_key:
            checkout_session.session_key = request.session.session_key or ""
            changed_fields.append("session_key")

        if changed_fields:
            changed_fields.append("updated_at")
            checkout_session.save(update_fields=changed_fields)

        return checkout_session

    return CheckoutSession.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or "",
        cart=cart,
        status=CheckoutSession.Status.ACTIVE,
        expires_at=now + timedelta(minutes=ttl_minutes),
    )


def calculate_coupon_discount(coupon, subtotal_toman: int) -> int:
    if not coupon or subtotal_toman <= 0:
        return 0

    if coupon.discount_type == Coupon.DiscountType.FIXED:
        discount = coupon.value

    elif coupon.discount_type == Coupon.DiscountType.PERCENT:
        discount = subtotal_toman * coupon.value // 100

        if coupon.max_discount_toman:
            discount = min(discount, coupon.max_discount_toman)

    else:
        discount = 0

    return min(discount, subtotal_toman)


def validate_coupon_for_cart(code: str, cart):
    """
    Returns: (coupon, error_message)
    """

    code = (code or "").strip()

    if not code:
        return None, "کد تخفیف وارد نشده است."

    subtotal_toman = cart.subtotal_toman
    now = timezone.now()

    coupon = Coupon.objects.filter(code__iexact=code).first()

    if not coupon or not coupon.is_active:
        return None, "کد تخفیف معتبر نیست."

    if coupon.starts_at and coupon.starts_at > now:
        return None, "زمان استفاده از این کد تخفیف هنوز شروع نشده است."

    if coupon.expires_at and coupon.expires_at < now:
        return None, "مهلت استفاده از این کد تخفیف تمام شده است."

    if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
        return None, "ظرفیت استفاده از این کد تخفیف تکمیل شده است."

    if subtotal_toman < coupon.min_order_amount_toman:
        return (
            None,
            f"حداقل مبلغ سفارش برای این کد تخفیف {format_toman(coupon.min_order_amount_toman)} است.",
        )

    discount_toman = calculate_coupon_discount(coupon, subtotal_toman)

    if discount_toman <= 0:
        return None, "این کد تخفیف برای این سفارش قابل اعمال نیست."

    return coupon, None


def build_checkout_summary(cart, coupon=None) -> CheckoutSummary:
    subtotal_toman = int(cart.subtotal_toman)
    items_count = int(cart.items_count)

    discount_toman = calculate_coupon_discount(coupon, subtotal_toman)

    tax_percent = int(getattr(settings, "CHECKOUT_TAX_PERCENT", 10))
    shipping_price_toman = int(getattr(settings, "CHECKOUT_SHIPPING_PRICE_TOMAN", 0))

    taxable_amount = max(subtotal_toman - discount_toman, 0)
    tax_toman = taxable_amount * tax_percent // 100

    total_toman = taxable_amount + tax_toman + shipping_price_toman

    return CheckoutSummary(
        items_count=items_count,
        subtotal_toman=subtotal_toman,
        discount_toman=discount_toman,
        tax_toman=tax_toman,
        shipping_price_toman=shipping_price_toman,
        total_toman=total_toman,
        coupon=coupon,
    )


def summary_to_json(summary: CheckoutSummary) -> dict:
    return {
        "items_count": summary.items_count,
        "subtotal_toman": summary.subtotal_toman,
        "discount_toman": summary.discount_toman,
        "tax_toman": summary.tax_toman,
        "shipping_price_toman": summary.shipping_price_toman,
        "total_toman": summary.total_toman,
        "subtotal_display": format_toman(summary.subtotal_toman),
        "discount_display": f"- {format_toman(summary.discount_toman)}",
        "tax_display": format_toman(summary.tax_toman),
        "shipping_display": (
            format_toman(summary.shipping_price_toman)
            if summary.shipping_price_toman
            else "پس‌کرایه"
        ),
        "total_display": format_toman(summary.total_toman),
    }