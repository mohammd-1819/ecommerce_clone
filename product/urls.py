from django.urls import path
from .views import ProductListView, ProductDetailView

app_name = 'product'


urlpatterns = [
    path('list/', ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
]