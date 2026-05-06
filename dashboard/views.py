import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from transactions.services import TransactionService
from budgets.services import BudgetService


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = '/auth/login/'
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['stats'] = TransactionService.get_dashboard_stats(user)
        context['recent_transactions'] = TransactionService.get_recent_transactions(user)
        category_rows = TransactionService.get_expense_by_category(user, limit=8)
        context['pie_labels'] = json.dumps([row['category__name'] for row in category_rows])
        context['pie_data'] = json.dumps([float(row['total'])   for row in category_rows])

        monthly_rows = TransactionService.get_monthly_income_vs_expense(user, months=6)
        context['bar_labels'] = json.dumps([row['label']   for row in monthly_rows])
        context['bar_income'] = json.dumps([row['income']  for row in monthly_rows])
        context['bar_expense'] = json.dumps([row['expense'] for row in monthly_rows])
        context['budget_summary'] = BudgetService.get_budget_summary(user)

        return context
