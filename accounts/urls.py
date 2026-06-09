from django.urls import path
from .views import ProfileDashboardView, ProfileOrdersView

app_name = 'accounts'


urlpatterns = [
    path('dashboard/', ProfileDashboardView.as_view(), name='profile-dashboard'),
    path('orders/', ProfileOrdersView.as_view(), name='profile-orders'),
]