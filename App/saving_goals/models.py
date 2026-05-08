"""
Database models for the saving_goals application.
Defines the structure and behavior of SavingGoal records.
"""
from django.db import models
from django.conf import settings


class SavingGoal(models.Model):
    """
    Represents a financial saving goal for a specific user.
    
    Attributes:
        user (ForeignKey): The owner of the saving goal.
        goal_name (CharField): The name/title of the goal.
        target_amount (DecimalField): The total amount of money to be saved.
        current_amount (DecimalField): The amount currently saved.
        deadline (DateField): The target date to reach the goal.
        status (CharField): Current status (In Progress or Completed).
        created_at (DateTimeField): Timestamp when the goal was created.
        updated_at (DateTimeField): Timestamp of the last update.
    """

    class Status(models.TextChoices):
        """Choices for the saving goal status."""
        IN_PROGRESS = "In Progress", "In Progress"
        COMPLETED   = "Completed",   "Completed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saving_goals")
    goal_name= models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deadline = models.DateField()
    status= models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata options for the SavingGoal model."""
        ordering = ["deadline"]
        verbose_name = "Saving Goal"
        verbose_name_plural = "Saving Goals"

    def __str__(self):
        """Returns a string representation of the SavingGoal."""
        return f"{self.goal_name} ({self.user})"