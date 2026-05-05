from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import Budget
from .forms import BudgetForm
from .services import BudgetService
from transactions.models import Category


@method_decorator(login_required, name='dispatch')
class BudgetListView(View):
    def get(self, request):
        budgets = BudgetService.get_user_budgets(request.user)
        return render(request, 'budgets/budget_list.html', {'budgets': budgets})


@method_decorator(login_required, name='dispatch')
class BudgetCreateView(View):
    def get(self, request):
        form = BudgetForm(request.user)
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Create'})

    def post(self, request):
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            BudgetService.create_budget(request.user, form)
            messages.success(request, 'Budget created!')
            return redirect('budgets:budget_list')
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Create'})


@method_decorator(login_required, name='dispatch')
class BudgetDetailView(View):
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        return render(request, 'budgets/budget_detail.html', {'budget': budget})


@method_decorator(login_required, name='dispatch')
class BudgetEditView(View):
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        form = BudgetForm(request.user, instance=budget)
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Save Changes'})

    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        form = BudgetForm(request.user, request.POST, instance=budget)
        if form.is_valid():
            BudgetService.update_budget(form)
            messages.success(request, 'Budget updated!')
            return redirect('budgets:budget_list')
        return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Save Changes'})


@method_decorator(login_required, name='dispatch')
class BudgetDeleteView(View):
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})

    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk, user=request.user)
        BudgetService.delete_budget(budget)
        messages.success(request, 'Budget deleted!')
        return redirect('budgets:budget_list')
