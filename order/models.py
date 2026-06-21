from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel


USER_ADDRESS_MODEL = "accounts.UserAddress"



class PaymentMethod(TimeStampedModel):
    code = models.SlugField(max_length=60, unique=True, allow_unicode=True, verbose_name="کد")
    title = models.CharField(max_length=120, verbose_name="عنوان")
    description = models.CharField(max_length=260, blank=True, verbose_name="توضیحات")
    is_online = models.BooleanField(default=True, verbose_name="پرداخت آنلاین")
    gateway_name = models.CharField(max_length=80, blank=True, verbose_name="نام درگاه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "روش پرداخت"
        verbose_name_plural = "روش‌های پرداخت"

    def __str__(self):
        return self.title


class Coupon(TimeStampedModel):
    class DiscountType(models.TextChoices):
        FIXED = "fixed", "مبلغ ثابت"
        PERCENT = "percent", "درصدی"

    code = models.CharField(max_length=40, unique=True, verbose_name="کد تخفیف")
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, verbose_name="نوع تخفیف")
    value = models.PositiveIntegerField(verbose_name="مقدار تخفیف")
    max_discount_toman = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="سقف تخفیف تومان")
    min_order_amount_toman = models.PositiveBigIntegerField(default=0, verbose_name="حداقل مبلغ سفارش تومان")

    starts_at = models.DateTimeField(null=True, blank=True, verbose_name="شروع اعتبار")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="پایان اعتبار")

    usage_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="محدودیت استفاده")
    used_count = models.PositiveIntegerField(default=0, verbose_name="تعداد استفاده شده")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

    def __str__(self):
        return self.code


class CheckoutSession(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "فعال"
        CONVERTED = "converted", "تبدیل شده به سفارش"
        EXPIRED = "expired", "منقضی شده"
        CANCELLED = "cancelled", "لغو شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="checkout_sessions",
        verbose_name="کاربر",
    )
    session_key = models.CharField(max_length=80, blank=True, db_index=True, verbose_name="کلید سشن")

    cart = models.ForeignKey(
        "cart.Cart",
        on_delete=models.PROTECT,
        related_name="checkout_sessions",
        verbose_name="سبد خرید",
    )

    selected_address = models.ForeignKey(
        USER_ADDRESS_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="checkout_sessions",
        verbose_name="آدرس انتخاب‌شده",
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="checkout_sessions",
        verbose_name="روش پرداخت",
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkout_sessions",
        verbose_name="کد تخفیف",
    )

    note = models.TextField(blank=True, verbose_name="توضیحات سفارش")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="وضعیت",
    )
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان انقضا")

    class Meta:
        verbose_name = "جلسه تکمیل خرید"
        verbose_name_plural = "جلسه‌های تکمیل خرید"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Checkout #{self.pk}"


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "در انتظار پرداخت"
        PAID = "paid", "پرداخت شده"
        PREPARING = "preparing", "در حال آماده‌سازی"
        SHIPPED = "shipped", "ارسال شده"
        DELIVERED = "delivered", "تحویل شده"
        CANCELLED = "cancelled", "لغو شده"
        REFUNDED = "refunded", "مرجوع شده"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "پرداخت نشده"
        PENDING = "pending", "در انتظار نتیجه پرداخت"
        PAID = "paid", "پرداخت موفق"
        FAILED = "failed", "پرداخت ناموفق"
        REFUNDED = "refunded", "بازگشت وجه"

    code = models.CharField(max_length=30, unique=True, db_index=True, verbose_name="شماره سفارش")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="کاربر",
    )
    checkout_session = models.OneToOneField(
        CheckoutSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
        verbose_name="جلسه تکمیل خرید",
    )
    cart = models.ForeignKey(
        "cart.Cart",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="سبد خرید",
    )

    address = models.ForeignKey(
        USER_ADDRESS_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="آدرس کاربر",
    )

    recipient_full_name = models.CharField(max_length=160, verbose_name="نام گیرنده")
    recipient_phone = models.CharField(max_length=20, verbose_name="شماره تماس گیرنده")
    province = models.CharField(max_length=80, blank=True, verbose_name="استان")
    city = models.CharField(max_length=80, blank=True, verbose_name="شهر")
    postal_address = models.TextField(verbose_name="آدرس کامل")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="کد پستی")

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="روش پرداخت",
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="کد تخفیف",
    )

    subtotal_toman = models.PositiveBigIntegerField(default=0, verbose_name="جمع قیمت کالاها")
    discount_toman = models.PositiveBigIntegerField(default=0, verbose_name="تخفیف")
    tax_toman = models.PositiveBigIntegerField(default=0, verbose_name="مالیات")
    shipping_price_toman = models.PositiveBigIntegerField(default=0, verbose_name="هزینه ارسال")
    total_toman = models.PositiveBigIntegerField(default=0, verbose_name="مبلغ قابل پرداخت")

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        db_index=True,
        verbose_name="وضعیت سفارش",
    )
    payment_status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_index=True,
        verbose_name="وضعیت پرداخت",
    )

    customer_note = models.TextField(blank=True, verbose_name="یادداشت مشتری")
    admin_note = models.TextField(blank=True, verbose_name="یادداشت مدیریت")

    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پرداخت")
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ارسال")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تحویل")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    def mark_paid(self):
        self.payment_status = self.PaymentStatus.PAID
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["payment_status", "status", "paid_at", "updated_at"])


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )

    product = models.ForeignKey(
        "product.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="محصول",
    )
    variant = models.ForeignKey(
        "product.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="تنوع محصول",
    )

    # Snapshot fields
    product_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="نام محصول در زمان سفارش",
    )
    variant_summary = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="مشخصات تنوع در زمان سفارش",
        help_text="مثلاً: ۲۵۰ گرم • آسیاب متوسط",
    )
    unit_price_toman = models.PositiveBigIntegerField(
        default=0,
        verbose_name="قیمت واحد در زمان سفارش",
    )

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="تعداد")
    line_total_toman = models.PositiveBigIntegerField(verbose_name="جمع این کالا")

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    @property
    def display_title(self):
        if self.product_title:
            return self.product_title

        if self.product_id and self.product:
            return self.product.title

        return "محصول حذف‌شده"

    @property
    def display_meta(self):
        parts = []

        if self.variant_summary:
            parts.append(self.variant_summary)

        parts.append(f"تعداد {self.quantity}")

        return " • ".join(parts)

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"


class PaymentTransaction(TimeStampedModel):
    class Status(models.TextChoices):
        INITIATED = "initiated", "شروع شده"
        PENDING = "pending", "در انتظار پرداخت"
        SUCCESS = "success", "موفق"
        FAILED = "failed", "ناموفق"
        CANCELLED = "cancelled", "لغو شده"
        REFUNDED = "refunded", "برگشت خورده"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="سفارش",
    )

    amount_toman = models.PositiveBigIntegerField(verbose_name="مبلغ تومان")
    gateway = models.CharField(max_length=80, blank=True, null=True ,verbose_name="درگاه پرداخت")

    authority = models.CharField(max_length=160, blank=True, db_index=True, verbose_name="کد authority")
    ref_id = models.CharField(max_length=160, blank=True, db_index=True, verbose_name="شماره پیگیری درگاه")
    tracking_code = models.CharField(max_length=160, blank=True, verbose_name="کد رهگیری")

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.INITIATED,
        db_index=True,
        verbose_name="وضعیت",
    )

    request_payload = models.JSONField(default=dict, blank=True, verbose_name="داده ارسالی")
    response_payload = models.JSONField(default=dict, blank=True, verbose_name="داده دریافتی")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پرداخت")

    class Meta:
        verbose_name = "تراکنش پرداخت"
        verbose_name_plural = "تراکنش‌های پرداخت"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.code} - {self.status}"