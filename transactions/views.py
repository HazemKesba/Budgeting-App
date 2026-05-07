"""Class-based views for transaction management and reporting."""
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import FormView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .forms import TransactionForm
from .models import Transaction, Category
from .services import TransactionService

class TransactionListView(LoginRequiredMixin, ListView):
    """Displays paginated transaction history with optional category filtering."""
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        """Filter transactions by owner and optional category query parameter."""
        qs = Transaction.objects.filter(user=self.request.user).select_related('category', 'savings_goal')
        category_id = self.request.GET.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def get_context_data(self, **kwargs):
        """Inject available categories and selected filter into template context."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(
            Q(user__isnull=True) | Q(user=self.request.user)
        )
        context['selected_category'] = self.request.GET.get('category', '')
        return context

class TransactionCreateView(LoginRequiredMixin, FormView):
    """Handles new transaction creation via plain form and service delegation."""
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:list')

    def get_form_kwargs(self):
        """Pass the authenticated user to the form for dynamic choice population."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """Pre-fill the date field with the current datetime."""
        initial = super().get_initial()
        initial['date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
        return initial

    def form_valid(self, form):
        """Delegate creation to service layer, handle errors, and redirect on success."""
        try:
            TransactionService.create_transaction(
                user=self.request.user,
                form_data=form.cleaned_data
            )
            messages.success(self.request, "Transaction created successfully!")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)

class TransactionUpdateView(LoginRequiredMixin, FormView):
    """Handles updating existing transactions with pre-filled form data."""
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """Populate form fields with existing transaction data."""
        txn = get_object_or_404(Transaction, id=self.kwargs['pk'], user=self.request.user)
        return {
            'transaction_type': txn.transaction_type,
            'amount': txn.amount,
            'description': txn.description,
            'category': txn.category.id if txn.category else '',
            'date': txn.date.strftime('%Y-%m-%dT%H:%M'),
            'payment_method': txn.payment_method,
            'note': txn.note,
            'savings_goal': txn.savings_goal.id if txn.savings_goal else '',
        }

    def form_valid(self, form):
        """Delegate update to service layer and handle validation/redirects."""
        try:
            TransactionService.update_transaction(
                txn_id=self.kwargs['pk'],
                user=self.request.user,
                form_data=form.cleaned_data
            )
            messages.success(self.request, "Transaction updated successfully!")
            return super().form_valid(form)
        except Transaction.DoesNotExist:
            messages.error(self.request, "Transaction not found.")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)

class TransactionDeleteView(LoginRequiredMixin, View):
    """Handles GET confirmation rendering and POST deletion with service delegation."""
    template_name = 'transactions/transaction_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        """Render deletion confirmation page with transaction details."""
        txn = get_object_or_404(Transaction, id=kwargs['pk'], user=request.user)
        return render(request, self.template_name, {'object': txn})

    def post(self, request, *args, **kwargs):
        """Execute deletion via service layer and redirect to transaction list."""
        try:
            TransactionService.delete_transaction(
                txn_id=kwargs['pk'],
                user=request.user
            )
            messages.success(request, "Transaction deleted successfully!")
        except Exception as e:
            messages.error(request, f"Failed to delete: {str(e)}")
        return redirect('transactions:list')