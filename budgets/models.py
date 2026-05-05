from django.db import models
from django.conf import settings


class Budget(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category        = models.ForeignKey("transactions.Category", on_delete=models.CASCADE)
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    start_date      = models.DateField()
    end_date        = models.DateField()
    alert_threshold = models.PositiveIntegerField(default=80)
    spent           = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # temporary for testing

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.category.name} - {self.amount}"  # shows "Food - 600" in admin

    def get_spent(self):
        try:
            from transactions.models import Transaction
            result = Transaction.objects.filter(
                user=self.user,
                category=self.category,
                date__gte=self.start_date,
                date__lte=self.end_date,
            ).aggregate(total=models.Sum('amount'))['total']
            return result or 0
        except:
            return self.spent  # uses manual field when transactions app doesn't exist

    def get_remaining(self):
        return self.amount - self.get_spent()  # 600 - 555 = 45

    def get_progress_percent(self):
        if self.amount == 0:
            return 0
        return round((self.get_spent() / self.amount) * 100, 1)  # (555/600)*100 = 93%

    def get_status(self):
        pct = self.get_progress_percent()
        if pct >= 100:
            return 'danger'   # over budget → red
        elif pct >= self.alert_threshold:
            return 'warning'  # near limit → orange  (uses YOUR alert % not hardcoded 80)
        return 'safe'         # all good → blue