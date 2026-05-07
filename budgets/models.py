"""
Budget models for the budgeting application.

Contains the `Budget` model which tracks spending limits, timeframes,
alert thresholds, and provides helper methods to calculate spending progress.
"""
from django.db import models
from django.conf import settings


class Budget(models.Model):
    """Represents a user-defined spending budget for a specific category and time period."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey("transactions.Category", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    alert_threshold = models.PositiveIntegerField(default=80)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-start_date']

    def __str__(self) -> str:
        return f"{self.category.name} - {self.amount}"

    def get_spent(self) -> float:
        """Calculate the total amount spent in this budget's category within the date range.

        Queries the `transactions` app for matching records. Falls back to the `spent` 
        field if the transactions app is unavailable or an error occurs.

        Returns:
            float: The total amount spent.
        """
        try:
            from transactions.models import Transaction
            result = Transaction.objects.filter(
                user=self.user,
                category=self.category,
                date__gte=self.start_date,
                date__lte=self.end_date,
            ).aggregate(total=models.Sum('amount'))['total']
            return result or 0
        except Exception:
            return self.spent

    def get_remaining(self) -> float:
        """Calculate the remaining budget amount.

        Returns:
            float: The difference between the budget amount and the amount spent.
        """
        return self.amount - self.get_spent()

    def get_progress_percent(self) -> float:
        """Calculate the percentage of the budget that has been spent.

        Returns:
            float: The spending progress as a percentage, rounded to one decimal place.
            Returns 0 if the budget amount is 0 to avoid division by zero.
        """
        if self.amount == 0:
            return 0
        return round((self.get_spent() / self.amount) * 100, 1)

    def get_status(self) -> str:
        """Determine the budget status based on spending progress and the alert threshold.

        Returns:
            str: 
                - ``'danger'`` if spending is 100% or over.
                - ``'warning'`` if spending meets or exceeds the alert threshold.
                - ``'safe'`` otherwise.
        """
        pct = self.get_progress_percent()
        if pct >= 100:
            return 'danger'
        elif pct >= self.alert_threshold:
            return 'warning'
        return 'safe'