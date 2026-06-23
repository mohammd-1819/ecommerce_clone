from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

from core.models import TimeStampedModel


class ProductCategory(TimeStampedModel):
    title = models.CharField(max_length=120, verbose_name="عنوان")
    slug = models.SlugField(max_length=160, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "دسته‌بندی محصول"
        verbose_name_plural = "دسته‌بندی محصولات"

    def __str__(self):
        return self.title


class Product(TimeStampedModel):
    
    class StockStatus(models.TextChoices):
        AVAILABLE = "available", "موجود"
        UNAVAILABLE = "unavailable", "نا موجود"

    class Badge(models.TextChoices):
        NONE = "", "بدون نشان"
        NEW = "new", "جدید"
        BESTSELLER = "bestseller", "پرفروش"
        SPECIAL = "special", "ویژه"

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی",
    )

    title = models.CharField(max_length=180, verbose_name="نام محصول")
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    base_sku = models.CharField(max_length=64, unique=True, verbose_name="کد پایه محصول")

    short_description = models.CharField(max_length=280, blank=True, verbose_name="توضیح کوتاه")
    description = models.TextField(blank=True, verbose_name="توضیحات کامل")

    main_image = models.ImageField(upload_to="products/main/", verbose_name="تصویر اصلی")
    badge = models.CharField(
        max_length=20,
        choices=Badge.choices,
        blank=True,
        default=Badge.NONE,
        verbose_name="نشان محصول",
    )
    stock_status = models.CharField(
        max_length=30,
        choices=StockStatus.choices,
        default=StockStatus.AVAILABLE,
        verbose_name="وضعیت موجودی",
    )
    order_counter = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, verbose_name="محصول منتخب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    meta_title = models.CharField(max_length=180, blank=True, verbose_name="عنوان سئو")
    meta_description = models.CharField(max_length=300, blank=True, verbose_name="توضیحات سئو")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]
        indexes = [
            # Main product list: active products ordered newest first
            models.Index(
                fields=["is_active", "-created_at"],
                name="product_active_created_idx",
            ),

            # Category product list: category + active + newest
            models.Index(
                fields=["category", "is_active", "-created_at"],
                name="product_cat_active_created_idx",
            ),

            # Related products in detail page
            models.Index(
                fields=["category", "is_active", "-is_featured", "-created_at"],
                name="product_related_idx",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def default_variant(self):
        return self.variants.filter(is_active=True, is_default=True).first() or self.variants.filter(is_active=True).first()

    @property
    def is_available(self):
        return self.variants.filter(is_active=True, stock_quantity__gt=0).exists()


class WeightOption(TimeStampedModel):
    title = models.CharField(max_length=80, verbose_name="عنوان نمایشی")
    value_grams = models.PositiveIntegerField(verbose_name="وزن به گرم")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "گزینه وزن"
        verbose_name_plural = "گزینه‌های وزن"
        constraints = [
            models.UniqueConstraint(fields=["value_grams"], name="unique_weight_value_grams"),
        ]

    def __str__(self):
        return self.title


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="محصول",
    )
    weight = models.ForeignKey(
        WeightOption,
        on_delete=models.PROTECT,
        related_name="variants",
        verbose_name="وزن",
    )

    sku = models.CharField(max_length=80, unique=True, verbose_name="کد کالا")
    price_toman = models.PositiveBigIntegerField(verbose_name="قیمت تومان")

    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="موجودی")

    is_default = models.BooleanField(default=False, verbose_name="گزینه پیش‌فرض")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "تنوع محصول"
        verbose_name_plural = "تنوع‌های محصول"
        ordering = ["product", "weight__value_grams"]
        constraints = [
            models.UniqueConstraint(fields=["product", "weight"], name="unique_product_weight_variant"),
        ]
        indexes = [
            # Helps active variant lookup per product
            models.Index(
                fields=["product", "is_active"],
                name="variant_product_active_idx",
            ),

            # Helps default variant lookup/subquery ordering partially
            models.Index(
                fields=["product", "is_active", "-is_default", "created_at"],
                name="variant_default_lookup_idx",
            ),

            # Helps stock availability checks if you use Product.is_available
            models.Index(
                fields=["product", "is_active", "stock_quantity"],
                name="variant_stock_lookup_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.weight.title}"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def final_price_toman(self):
        return self.price_toman


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="محصول",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
        verbose_name="تنوع محصول",
    )
    image = models.ImageField(upload_to="products/gallery/", verbose_name="تصویر")
    alt_text = models.CharField(max_length=180, verbose_name="متن جایگزین تصویر")
    is_main = models.BooleanField(default=False, verbose_name="تصویر اصلی")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        indexes = [
            models.Index(
                fields=["product", "-is_main", "created_at"],
                name="prod_img_order_idx",
            ),
            models.Index(
                fields=["variant", "created_at"],
                name="prod_img_variant_idx",
            ),
        ]

    def __str__(self):
        return self.alt_text


class ProductAttribute(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name="محصول",
    )
    title = models.CharField(max_length=120, verbose_name="عنوان ویژگی")
    value = models.CharField(max_length=240, verbose_name="مقدار ویژگی")

    class Meta:
        verbose_name = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصول"
        indexes = [
            models.Index(
                fields=["product", "created_at"],
                name="attr_product_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title}: {self.value}"


class ProductReview(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="محصول",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_reviews",
        verbose_name="کاربر",
    )

    first_name = models.CharField(max_length=255, verbose_name="نام")
    last_name = models.CharField(max_length=255, verbose_name="نام خانوادگی")
    body = models.TextField(verbose_name="متن دیدگاه")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )
    is_verified_purchase = models.BooleanField(default=False, verbose_name="خرید تأیید شده")

    class Meta:
        verbose_name = "دیدگاه محصول"
        verbose_name_plural = "دیدگاه‌های محصول"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["product", "status", "-created_at"],
                name="review_product_status_idx",
            ),
        ]
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.product.title} - {self.full_name}"