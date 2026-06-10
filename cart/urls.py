from django.urls import path
from .views import CartView

app_name = 'cart'


urlpatterns = [
    path('detail/', CartView.as_view(), name='cart-detail')
]