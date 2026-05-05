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