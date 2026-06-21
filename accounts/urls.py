from django.urls import path
from .views import ProfileDashboardView, UserOrderListView, ProfileAddressView, ProfileCommentsView, ProfileEditView

app_name = 'accounts'


urlpatterns = [
    path('dashboard/', ProfileDashboardView.as_view(), name='profile-dashboard'),
    path('orders/', UserOrderListView.as_view(), name='profile-orders'),
    path('address/', ProfileAddressView.as_view(), name='profile-address'),
    path('comments/', ProfileCommentsView.as_view(), name='profile-comments'),
    path('edit/', ProfileEditView.as_view(), name='profile-edit'),
]