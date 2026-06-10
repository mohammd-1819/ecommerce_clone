from django.urls import path
from .views import OrderDetailView

app_name = 'order'


urlpatterns = [
    path('detail/', OrderDetailView.as_view(), name='order-detail')
]