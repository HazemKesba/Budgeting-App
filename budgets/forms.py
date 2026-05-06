from django import forms

from transactions.models import Category
from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'start_date', 'end_date', 'alert_threshold', 'spent']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # show categories with no user (general) AND this user's categories
        self.fields['category'].queryset = Category.objects.filter(
            user=user
        ) | Category.objects.filter(
            user=None
        )