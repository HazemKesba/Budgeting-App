"""Django admin configuration for transaction management."""
from django.contrib import admin
from .models import Transaction, Category

admin.site.register(Transaction)
admin.site.register(Category)