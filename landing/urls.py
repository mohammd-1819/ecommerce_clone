from django.urls import path
from .views import LandingView, AboutView, ContactRequestCreateView, ProductSearchModalView

app_name = 'landing'


urlpatterns = [
    path('', LandingView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactRequestCreateView.as_view(), name='contact'),
    path("search/",ProductSearchModalView.as_view(),name="product-search-modal"),
]