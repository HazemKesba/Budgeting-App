from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    """Manager for the CustomUser model handling user and superuser creation."""

    def create_user(self, email, full_name, password=None, **extra_fields):
        """Create and save a regular user with the given email and password.
        
        Args:
            email: The user's email address.
            full_name: The user's full name.
            password: The user's raw password.
            **extra_fields: Additional fields passed to the user model.
            
        Returns:
            The created CustomUser instance.
            
        Raises:
            ValueError: If the email field is not provided.
        """
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """Create and save a superuser with elevated permissions.
        
        Args:
            email: The superuser's email address.
            full_name: The superuser's full name.
            password: The superuser's password.
            **extra_fields: Additional fields passed to the user model.
            
        Returns:
            The created CustomUser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, full_name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model that uses email as the primary authentication identifier.
    
    Replaces Django's default User model to support full_name and email-based login.
    """
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        """Return the string representation of the user."""
        return self.full_name