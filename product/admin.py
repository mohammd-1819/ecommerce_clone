from django.contrib import admin

from .models import (
    ProductCategory,
    Product,
    WeightOption,
    ProductVariant,
    ProductImage,
    ProductAttribute,
    ProductReview
)


admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(WeightOption)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
admin.site.register(ProductAttribute)
admin.site.register(ProductReview)
