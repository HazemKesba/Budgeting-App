from django import forms
from .models import Category, TRANSACTION_TYPES, PAYMENT_METHODS
from django.core.exceptions import ValidationError

class TransactionForm(forms.Form):
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES, widget=forms.RadioSelect)
    amount = forms.DecimalField(decimal_places=2)
    description = forms.CharField(max_length=200)
    category = forms.ChoiceField(choices=[])
    date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS)
    note = forms.CharField(widget=forms.Textarea, required=False)