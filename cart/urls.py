from django.urls import path
from .views import CartView, CechkoutView

app_name = 'cart'


urlpatterns = [
    path('detail/', CartView.as_view(), name='cart-detail'),
    path('checkout/', CechkoutView.as_view(), name='cart-checkout'),
]