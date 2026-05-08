from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class UserService:
    """Service layer for user-related business logic and database operations."""

    @classmethod
    @transaction.atomic
    def create_user(cls, full_name: str, email: str, password: str):
        """Create a new user account within an atomic transaction.
        
        Args:
            full_name: The user's full name.
            email: The user's email address.
            password: The user's raw password (automatically hashed).
            
        Returns:
            User: The newly created and saved user instance.
        """
        user = User.objects.create_user(
            email=email,
            full_name=full_name,
            password=password
        )
        return user