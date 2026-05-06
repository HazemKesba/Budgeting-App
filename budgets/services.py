from .models import Budget
from transactions.models import Category


class BudgetService:

    @staticmethod
    def get_user_budgets(user):
        """Get all budgets for a user with spending data attached."""
        return Budget.objects.filter(user=user).select_related('category')

    @staticmethod
    def get_budget(pk, user):
        """Get a single budget — only if it belongs to this user."""
        return Budget.objects.get(pk=pk, user=user)

    @staticmethod
    def create_budget(user, form):
        """Save a new budget from a valid form."""
        budget = form.save(commit=False)
        budget.user = user
        budget.save()
        return budget

    @staticmethod
    def update_budget(form):
        """Save changes to an existing budget."""
        return form.save()

    @staticmethod
    def delete_budget(budget):
        """Delete a budget."""
        budget.delete()

    @staticmethod
    def get_budget_summary(user):
        """
        Return summary counts for the user's budgets.
        Used by the dashboard to show how many budgets are safe / near-limit / exceeded.
        Returns a dict: {total, safe, warning, danger}
        """
        budgets = Budget.objects.filter(user=user).select_related('category')
        summary = {'total': 0, 'safe': 0, 'warning': 0, 'danger': 0}
        for b in budgets:
            summary['total'] += 1
            summary[b.get_status()] += 1
        return summary

    @staticmethod
    def get_user_categories(user):
        """Get all categories belonging to this user."""
        return Category.objects.filter(user=user)