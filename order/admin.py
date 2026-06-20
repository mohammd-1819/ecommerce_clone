from django.contrib import admin
from .models import PaymentMethod, Coupon, CheckoutSession, Order, OrderItem, PaymentTransaction


admin.site.register(PaymentMethod)
admin.site.register(Coupon)
admin.site.register(CheckoutSession)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PaymentTransaction)


