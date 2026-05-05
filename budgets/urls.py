from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    # Budget CRUD
    path('', views.budget_list, name='budget_list'),
    path('create/', views.budget_create, name='budget_create'),
    path('<int:pk>/', views.budget_detail, name='budget_detail'),
    path('<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('<int:pk>/delete/', views.budget_delete, name='budget_delete'),

    # Category CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]