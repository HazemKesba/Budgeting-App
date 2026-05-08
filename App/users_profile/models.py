"""User profile models for extended account information."""
from django.db import models
from django.conf import settings  

class Profile(models.Model):
    """Extends the CustomUser model with optional personal information.
    
    Maintains a one-to-one relationship with the authenticated user.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        """Return a readable string representation of the profile."""
        return f"{self.user.full_name}'s Profile"