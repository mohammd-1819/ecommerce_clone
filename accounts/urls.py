from django.urls import path
from .views import ProfileDashboardView, ProfileOrdersView, ProfileAddressView

app_name = 'accounts'


urlpatterns = [
    path('dashboard/', ProfileDashboardView.as_view(), name='profile-dashboard'),
    path('orders/', ProfileOrdersView.as_view(), name='profile-orders'),
    path('address/', ProfileAddressView.as_view(), name='profile-address'),
]