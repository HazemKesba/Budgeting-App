"""
URL configuration for the budgets application.

Maps URL routes to class-based views for managing budgets.
All routes are namespaced under ``'budgets'`` for reverse URL resolution.

Routes:
    - ``/``: List all budgets for the current user.
    - ``/create/``: Form to create a new budget.
    - ``/<int:pk>/``: Detail view for a specific budget.
    - ``/<int:pk>/edit/``: Form to edit an existing budget.
    - ``/<int:pk>/delete/``: View to confirm and delete a budget.
"""
from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.BudgetListView.as_view(), name='budget_list'),
    path('create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('<int:pk>/edit/', views.BudgetEditView.as_view(), name='budget_edit'),
    path('<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
]