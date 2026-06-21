from django.urls import path
from .views import ProfileDashboardView, UserOrderListView, ProfileAddressView, ProfileProductReviewListView, UserProfileEditView, LoginView

app_name = 'accounts'


urlpatterns = [
    path('dashboard/', ProfileDashboardView.as_view(), name='profile-dashboard'),
    path('orders/', UserOrderListView.as_view(), name='profile-orders'),
    path('address/', ProfileAddressView.as_view(), name='profile-address'),
    path('comments/', ProfileProductReviewListView.as_view(), name='profile-comments'),
    path('edit/', UserProfileEditView.as_view(), name='profile-edit'),
    path('login/', LoginView.as_view(), name='login'),
]