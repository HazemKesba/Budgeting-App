from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from transactions.services import TransactionService

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = TransactionService.get_dashboard_stats(self.request.user)
        context['recent_transactions'] = TransactionService.get_recent_transactions(self.request.user)
        return context