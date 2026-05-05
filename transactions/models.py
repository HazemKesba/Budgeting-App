from django.db import models
from datetime import datetime

TRANSACTION_TYPES = [
    ('income', 'Income'),
    ('expense', 'Expense'),
]

PAYMENT_METHODS = [
    ('cash', 'Cash'),
    ('card', 'Card'),
]

# Create your models here.
class Category(models.Model):
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="custom_categories"
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"],
                name='unique_category_per_user'
            )
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(
        "transactions.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date = models.DateTimeField(default=datetime.now)
    payment_method = models.CharField(choices=PAYMENT_METHODS)
    note = models.TextField(blank=True, default="")
    savings_goal = models.ForeignKey(
        'saving_goals.SavingGoal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.amount} ({self.description})"
    