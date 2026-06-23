import factory
from factory.django import DjangoModelFactory

from product.models import (
    Product,
    ProductAttribute,
    ProductCategory,
    ProductImage,
    ProductReview,
    ProductVariant,
    WeightOption,
)


class ProductCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ProductCategory

    title = factory.Sequence(lambda n: f"دسته‌بندی {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")
    is_active = True


class WeightOptionFactory(DjangoModelFactory):
    class Meta:
        model = WeightOption
        django_get_or_create = ("value_grams",)

    value_grams = factory.Sequence(lambda n: (n + 1) * 250)
    title = factory.LazyAttribute(lambda obj: f"{obj.value_grams} گرم")
    is_active = True


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(ProductCategoryFactory)

    title = factory.Sequence(lambda n: f"محصول تستی {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    base_sku = factory.Sequence(lambda n: f"BASE-SKU-{n}")

    short_description = "توضیح کوتاه محصول"
    description = "توضیحات کامل محصول"

    main_image = factory.django.ImageField(color="blue")

    badge = Product.Badge.NONE
    stock_status = Product.StockStatus.AVAILABLE

    order_counter = 0
    is_featured = False
    is_active = True

    meta_title = ""
    meta_description = ""


class ProductVariantFactory(DjangoModelFactory):
    class Meta:
        model = ProductVariant

    product = factory.SubFactory(ProductFactory)
    weight = factory.SubFactory(WeightOptionFactory)

    sku = factory.Sequence(lambda n: f"SKU-{n}")
    price_toman = 250_000
    stock_quantity = 10

    is_default = False
    is_active = True


class ProductImageFactory(DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    variant = None

    image = factory.django.ImageField(color="green")
    alt_text = factory.Sequence(lambda n: f"تصویر محصول {n}")
    is_main = False


class ProductAttributeFactory(DjangoModelFactory):
    class Meta:
        model = ProductAttribute

    product = factory.SubFactory(ProductFactory)
    title = factory.Sequence(lambda n: f"ویژگی {n}")
    value = factory.Sequence(lambda n: f"مقدار {n}")


class ProductReviewFactory(DjangoModelFactory):
    class Meta:
        model = ProductReview

    product = factory.SubFactory(ProductFactory)
    user = None

    first_name = "علی"
    last_name = "رضایی"
    body = "کیفیت محصول خوب بود."

    status = ProductReview.Status.PENDING
    is_verified_purchase = False