"""Forms for updating user account details and extended profile information."""
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    """Form for updating core user account fields (email and full name)."""
    class Meta:
        model = User
        fields = ['email', 'full_name']

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating extended profile details (bio, location, birth date)."""
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date']