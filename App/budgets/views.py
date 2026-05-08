"""
Views for the budgets application.

Contains class-based views handling CRUD operations for user budgets.
All views require authentication and delegate business logic to ``BudgetService``.
"""
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .models import Budget
from .forms import BudgetForm
from .services import BudgetService


@method_decorator(login_required, name='dispatch')
class BudgetListView(View):
    """Display a list of budgets for the authenticated user."""
    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle GET request to retrieve and display user budgets.

        Args:
            request: The current HTTP request.

        Returns:
            Rendered budget list page.
        """
        budgets = BudgetService.get_user_budgets(request.user)
        return render(request, 'budgets/budget_list.html', {'budgets': budgets})


@method_decorator(login_required, name='dispatch')
class BudgetCreateView(View):
    """Handle creation of new budgets via form submission."""
    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the budget creation form.

        Args:
            request: The current HTTP request.

        Returns:
            Rendered form page with 'Create' action label.
        """
        form = BudgetForm(request.user)
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Create'})

    def post(self, request: HttpRequest) -> HttpResponse:
        """Validate and save a new budget.

        Args:
            request: The current HTTP request containing form data.

        Returns:
            Redirect to budget list on success, or re-rendered form with validation errors.
        """
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            BudgetService.create_budget(request.user, form)
            messages.success(request, 'Budget created!')
            return redirect('budgets:budget_list')
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Create'})


@method_decorator(login_required, name='dispatch')
class BudgetDetailView(View):
    """Display detailed information for a single budget."""
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Retrieve and render a specific budget.

        Args:
            request: The current HTTP request.
            pk: Primary key of the budget to display.

        Returns:
            Rendered budget detail page.
        """
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        return render(request, 'budgets/budget_detail.html', {'budget': budget})


@method_decorator(login_required, name='dispatch')
class BudgetEditView(View):
    """Handle editing of existing budgets via form submission."""
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Render the budget editing form pre-filled with existing data.

        Args:
            request: The current HTTP request.
            pk: Primary key of the budget to edit.

        Returns:
            Rendered form page with 'Save Changes' action label.
        """
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        form = BudgetForm(request.user, instance=budget)
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Save Changes'})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Validate and apply updates to an existing budget.

        Args:
            request: The current HTTP request containing updated form data.
            pk: Primary key of the budget to update.

        Returns:
            Redirect to budget list on success, or re-rendered form with validation errors.
        """
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        form = BudgetForm(request.user, request.POST, instance=budget)
        if form.is_valid():
            BudgetService.update_budget(form)
            messages.success(request, 'Budget updated!')
            return redirect('budgets:budget_list')
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Save Changes'})


@method_decorator(login_required, name='dispatch')
class BudgetDeleteView(View):
    """Handle deletion of budgets with confirmation."""
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Render the budget deletion confirmation page.

        Args:
            request: The current HTTP request.
            pk: Primary key of the budget to delete.

        Returns:
            Rendered confirmation page.
        """
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Delete the specified budget and redirect.

        Args:
            request: The current HTTP request.
            pk: Primary key of the budget to delete.

        Returns:
            Redirect to budget list with success message.
        """
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        BudgetService.delete_budget(budget)
        messages.success(request, 'Budget deleted!')
        return redirect('budgets:budget_list')