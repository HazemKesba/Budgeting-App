"""Django admin configuration for custom user management."""
from django.contrib import admin
from .models import CustomUser

admin.site.register(CustomUser)