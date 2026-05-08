"""Form definitions for transaction creation and editing."""
from django import forms
from .models import Category, TRANSACTION_TYPES, PAYMENT_METHODS
from django.db.models import Q

class TransactionForm(forms.Form):
    """Plain form for transaction data entry with dynamic dropdown population."""
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES, widget=forms.RadioSelect)
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    description = forms.CharField(max_length=200)
    category = forms.ChoiceField(choices=[], required=False)
    date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS)
    note = forms.CharField(widget=forms.Textarea, required=False)
    savings_goal = forms.ChoiceField(choices=[], required=False, label="None (optional)")
    new_category = forms.CharField(max_length=50, required=False, label="Or create a new category")

    def __init__(self, *args, user=None, **kwargs):
        """Initialize form fields and populate category/savings goal choices for the authenticated user."""
        super().__init__(*args, **kwargs)

        if user:
            categories = Category.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            ).values_list("id", "name")
            self.fields["category"].choices = [('', 'Select a category')] + list(categories)

            try:
                from saving_goals.models import SavingGoal
                goals = SavingGoal.objects.filter(user=user).exclude(status='completed').values_list('id', 'goal_name')
                self.fields["savings_goal"].choices = [('', 'None (optional)')] + list(goals)
            except ImportError:
                self.fields['savings_goal'].widget = forms.HiddenInput()

    def clean(self):
        """Validate form data, enforce category requirement, and restrict savings goals to income transactions."""
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        savings_goal = cleaned_data.get('savings_goal')
        new_category = cleaned_data.get('new_category')
        category = cleaned_data.get('category')

        if transaction_type == 'expense' and savings_goal:
            raise forms.ValidationError('Saving goals can only be linked to transactions of type (Income).')
        
        if new_category and not category:
            cleaned_data['new_category_name'] = new_category.strip()
        elif not new_category and not category:
            raise forms.ValidationError('A category must be added.')
        
        return cleaned_data