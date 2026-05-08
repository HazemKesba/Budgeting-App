"""
Django admin configuration for the budgets application.

Registers the ``Budget`` model with the Django admin interface,
enabling authorized users to manage budget records directly from the admin panel.
"""
from django.contrib import admin
from .models import Budget

admin.site.register(Budget)