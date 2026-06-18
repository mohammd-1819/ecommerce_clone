from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from core.models import TimeStampedModel
from product.models import ProductVariant


class Cart(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "فعال"
        ORDERED = "ordered", "تبدیل شده به سفارش"
        ABANDONED = "abandoned", "رها شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name="کاربر",
    )
    session_key = models.CharField(max_length=80, blank=True, db_index=True, verbose_name="کلید سشن")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="وضعیت",
    )

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="active", user__isnull=False),
                name="unique_active_cart_per_user",
            ),
            models.UniqueConstraint(
                fields=["session_key"],
                condition=Q(status="active") & ~Q(session_key=""),
                name="unique_active_cart_per_session",
            ),
        ]

    def __str__(self):
        return f"Cart #{self.pk}"

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal_toman(self):
        return sum(item.line_total_toman for item in self.items.select_related("variant"))


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سبد خرید",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="cart_items",
        verbose_name="تنوع محصول",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="تعداد",
    )

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        constraints = [
            models.UniqueConstraint(fields=["cart", "variant"], name="unique_variant_per_cart"),
        ]

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

    @property
    def unit_price_toman(self):
        return self.variant.final_price_toman

    @property
    def line_total_toman(self):
        return self.unit_price_toman * self.quantity