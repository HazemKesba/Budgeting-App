from django.urls import path
from .views import TransactionListView, TransactionCreateView, TransactionUpdateView, TransactionDeleteView

app_name = 'transactions'

urlpatterns = [
    path('', TransactionListView.as_view(), name='list'),
    path('add/', TransactionCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', TransactionUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', TransactionDeleteView.as_view(), name='delete'),
]