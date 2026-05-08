"""
Service layer for budget-related business logic.

Contains the ``BudgetService`` class, which provides static methods
for querying, creating, updating, deleting, and summarizing user budgets.
"""
from django.db.models import QuerySet
from django import forms

from .models import Budget
from transactions.models import Category


class BudgetService:
    """Static utility class for budget operations.

    Encapsulates database queries and business logic to keep views thin.
    """

    @staticmethod
    def get_user_budgets(user) -> QuerySet[Budget]:
        """Retrieve all budgets associated with a specific user.

        Args:
            user: The authenticated user instance.

        Returns:
            A queryset of ``Budget`` objects with their related ``Category`` pre-fetched.
        """
        return Budget.objects.filter(user=user).select_related('category')

    @staticmethod
    def get_budget(pk: int, user) -> Budget:
        """Retrieve a single budget by primary key, scoped to the given user.

        Args:
            pk: The primary key of the budget.
            user: The authenticated user instance.

        Returns:
            The matching ``Budget`` instance.

        Raises:
            Budget.DoesNotExist: If no budget matches the provided ``pk`` and ``user``.
        """
        return Budget.objects.get(pk=pk, user=user)

    @staticmethod
    def create_budget(user, form: forms.ModelForm) -> Budget:
        """Create and save a new budget from a validated form.

        Args:
            user: The authenticated user instance.
            form: A validated ``BudgetForm`` instance (saved with ``commit=False``).

        Returns:
            The newly saved ``Budget`` instance.
        """
        budget = form.save(commit=False)
        budget.user = user
        budget.save()
        return budget

    @staticmethod
    def update_budget(form: forms.ModelForm) -> Budget:
        """Save changes to an existing budget instance.

        Args:
            form: A validated ``BudgetForm`` instance bound to an existing ``Budget``.

        Returns:
            The updated ``Budget`` instance.
        """
        return form.save()

    @staticmethod
    def delete_budget(budget: Budget) -> None:
        """Permanently delete a budget instance.

        Args:
            budget: The ``Budget`` instance to delete.
        """
        budget.delete()

    @staticmethod
    def get_budget_summary(user) -> dict[str, int]:
        """Calculate a summary of budget statuses for a user.

        Iterates through all user budgets and counts how many fall into
        ``safe``, ``warning``, or ``danger`` categories based on spending progress.

        Args:
            user: The authenticated user instance.

        Returns:
            A dictionary with keys ``total``, ``safe``, ``warning``, and ``danger``,
            mapped to their respective integer counts.
        """
        budgets = Budget.objects.filter(user=user).select_related('category')
        summary = {'total': 0, 'safe': 0, 'warning': 0, 'danger': 0}
        for b in budgets:
            summary['total'] += 1
            summary[b.get_status()] += 1
        return summary

    @staticmethod
    def get_user_categories(user) -> QuerySet[Category]:
        """Retrieve all categories owned by a specific user.

        Args:
            user: The authenticated user instance.

        Returns:
            A queryset of ``Category`` objects filtered by the given user.
        """
        return Category.objects.filter(user=user)