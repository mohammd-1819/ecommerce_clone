from django.urls import path
from .views import HomeView, AboutView, ContactRequestCreateView

app_name = 'landing'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactRequestCreateView.as_view(), name='contact'),
]