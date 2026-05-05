from django import forms
from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'start_date', 'end_date', 'alert_threshold', 'spent']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # only show THIS user's categories in the dropdown
        self.fields['category'].queryset = Category.objects.filter(user=user)