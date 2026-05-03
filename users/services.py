from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class UserService:

    @classmethod
    @transaction.atomic
    def create_user(cls, full_name: str, email: str, password: str):
        user = User.objects.create_user(
            email=email,
            full_name= full_name,
            password=password
        )
        return user