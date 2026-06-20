from django.urls import path
from .views import OrderDetailView, CheckoutDetailView, CouponApplyView, CheckoutAddressSaveView

app_name = 'order'


urlpatterns = [
    path("", CheckoutDetailView.as_view(), name="checkout-detail"),
    path("coupon/apply/", CouponApplyView.as_view(), name="coupon-apply"),
    path("address/save/", CheckoutAddressSaveView.as_view(), name="address-save"),

    path('detail/', OrderDetailView.as_view(), name='order-detail'),
]