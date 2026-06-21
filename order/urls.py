from django.urls import path
from .views import UserOrderDetailView, CheckoutDetailView, CouponApplyView, CheckoutAddressSaveView

app_name = 'order'


urlpatterns = [
    path("", CheckoutDetailView.as_view(), name="checkout-detail"),
    path("coupon/apply/", CouponApplyView.as_view(), name="coupon-apply"),
    path("address/save/", CheckoutAddressSaveView.as_view(), name="address-save"),

        path("<str:order_code>/",UserOrderDetailView.as_view(),name="order-detail",
    ),
]