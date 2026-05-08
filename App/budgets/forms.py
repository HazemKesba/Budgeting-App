"""
Forms for the budgets application.

Contains `BudgetForm` for creating and updating budget records,
with dynamic category filtering based on the current user.
"""
from django import forms

from transactions.models import Category
from .models import Budget


class BudgetForm(forms.ModelForm):
    """ModelForm for creating and updating `Budget` instances.

    Dynamically restricts the category dropdown to show only those
    owned by the current user or marked as general (user=None).
    """
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'start_date', 'end_date', 'alert_threshold']

    def __init__(self, user, *args, **kwargs) -> None:
        """Initialize the form and set a user-specific category queryset.

        Args:
            user: The authenticated user instance.
            *args: Positional arguments passed to the parent ``ModelForm``.
            **kwargs: Keyword arguments passed to the parent ``ModelForm``.
        """
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = (
            Category.objects.filter(user=user) | Category.objects.filter(user=None)
        )