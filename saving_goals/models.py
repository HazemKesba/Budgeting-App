from django.db import models
from django.conf import settings


class SavingGoal(models.Model):

    class Status(models.TextChoices):
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
        ordering = ["deadline"]
        verbose_name = "Saving Goal"
        verbose_name_plural = "Saving Goals"

    def __str__(self):
        return f"{self.goal_name} ({self.user})"