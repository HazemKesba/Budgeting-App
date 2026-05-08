"""
Application configuration for the budgets app.

Registers the ``budgets`` application with Django's app registry and
provides a central entry point for app-level initialization if needed.
"""
from django.apps import AppConfig


class BudgetsConfig(AppConfig):
    """Configuration class for the budgets application.

    Defines the application label and can be extended with a ``ready()`` method
    for tasks like connecting signals or verifying dependencies.
    """
    name = 'budgets'