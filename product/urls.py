from django.urls import path
from .views import ProductListView, ProductDetailView, ProductReviewCreateView

app_name = 'product'


urlpatterns = [
    path('list/', ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
        path("<slug:slug>/comments/",ProductReviewCreateView.as_view(),name="product-review-create",),
]