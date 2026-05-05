from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget, Category
from .forms import BudgetForm, CategoryForm

# ── Budget Views ──────────────────────────────────────────────────────────────

@login_required
def budget_list(request):
    # gets all budgets belonging to the logged in user
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budgets/budget_list.html', {'budgets': budgets})


@login_required
def budget_create(request):
    if request.method == 'POST':
        # user submitted the form
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)  # don't save to DB yet
            budget.user = request.user        # attach the logged in user
            budget.save()                     # now save to DB
            messages.success(request, 'Budget created!')
            return redirect('budgets:budget_list')
    else:
        # user just opened the page, show empty form
        form = BudgetForm(request.user)
    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Create'})


@login_required
def budget_detail(request, pk):
    # pk is the budget id from the URL e.g. /budgets/3/
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    return render(request, 'budgets/budget_detail.html', {'budget': budget})


@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST, instance=budget)  # instance = edit existing
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated!')
            return redirect('budgets:budget_list')
    else:
        form = BudgetForm(request.user, instance=budget)  # pre-fill form with existing data
    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Save Changes'})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted!')
        return redirect('budgets:budget_list')
    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})


# ── Category Views ────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'budgets/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created!')
            return redirect('budgets:category_list')
    else:
        form = CategoryForm()
    return render(request, 'budgets/category_form.html', {'form': form, 'action': 'Create'})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated!')
            return redirect('budgets:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'budgets/category_form.html', {'form': form, 'action': 'Save'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted!')
        return redirect('budgets:category_list')
    return render(request, 'budgets/category_confirm_delete.html', {'category': category})