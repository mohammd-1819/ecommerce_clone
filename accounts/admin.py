from django.contrib import admin
from .models import User, UserAddress, UserProfile

admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(UserProfile)
