"""
Admin configuration for the saving_goals application.
This module registers the SavingGoal model with the Django admin site.
"""
from django.contrib import admin
from .models import SavingGoal

admin.site.register(SavingGoal)