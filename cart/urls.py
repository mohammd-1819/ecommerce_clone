from django.urls import path
from .views import (
    AddToCartView,
    CartDetailView,
    RemoveFromCartView,
    UpdateCartItemQuantityView,
    CechkoutView
)

app_name = 'cart'


urlpatterns = [
    path("", CartDetailView.as_view(), name="cart-detail"),

    # Product detail form will use this one.
    path("add/", AddToCartView.as_view(), name="cart-add"),

    # Optional direct variant URL, still useful elsewhere.
    path("add/<int:variant_id>/", AddToCartView.as_view(), name="cart-add-variant"),

    path("update/<int:variant_id>/", UpdateCartItemQuantityView.as_view(), name="cart-update"),
    path("remove/<int:variant_id>/", RemoveFromCartView.as_view(), name="cart-remove"),

    path('checkout/', CechkoutView.as_view(), name='cart-checkout'),
]