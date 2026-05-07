"""Business logic layer for transactions, dashboard aggregates, and reporting."""
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import Transaction, Category
from django.db.models import F, Q, Sum

class TransactionService:
    """Handles transaction CRUD operations, goal balance synchronization, and analytics."""

    @classmethod
    @transaction.atomic
    def create_transaction(cls, user, form_data: dict):
        """Create a transaction and update linked savings goal balance if applicable.
        
        Args:
            user: Authenticated CustomUser instance.
            form_ Cleaned dictionary from TransactionForm.
            
        Returns:
            Transaction: The newly saved transaction instance.
        """
        from saving_goals.models import SavingGoal
        
        category = None
        if form_data.get('new_category_name'):
            category, _ = Category.objects.get_or_create(
                name=form_data['new_category_name'],
                user=user
            )
        elif form_data.get('category'):
            try:
                category = Category.objects.get(id=int(form_data['category']))
            except (Category.DoesNotExist, ValueError, TypeError):
                category = None
        
        savings_goal = None
        goal_id = form_data.get('savings_goal')
        if goal_id and goal_id != '':
            try:
                savings_goal = SavingGoal.objects.get(id=goal_id, user=user)
            except SavingGoal.DoesNotExist:
                pass
        
        txn = Transaction.objects.create(
            user=user,
            transaction_type=form_data['transaction_type'],
            amount=form_data['amount'],
            description=form_data['description'],
            category=category,
            date=form_data['date'],
            payment_method=form_data['payment_method'],
            note=form_data.get('note', ''),
            savings_goal=savings_goal
        )

        if txn.transaction_type == 'income' and txn.savings_goal:
            goal = txn.savings_goal
            goal.current_amount += txn.amount
            goal.save(update_fields=['current_amount'])

        return txn

    @classmethod
    @transaction.atomic
    def update_transaction(cls, txn_id, user, form_data: dict):
        """Update an existing transaction and adjust goal balances if income linkage changed.
        
        Args:
            txn_id: Primary key of the transaction to update.
            user: Authenticated user owning the transaction.
            form_ Cleaned dictionary from TransactionForm.
            
        Returns:
            Transaction: The updated transaction instance.
        """
        txn = Transaction.objects.get(id=txn_id, user=user)
        
        old_amount = txn.amount
        old_goal = txn.savings_goal
        old_type = txn.transaction_type
        
        category = None
        if form_data.get('new_category_name'):
            category, _ = Category.objects.get_or_create(
                name=form_data['new_category_name'],
                user=user
            )
        elif form_data.get('category'):
            try:
                category = Category.objects.get(id=int(form_data['category']))
            except (Category.DoesNotExist, ValueError, TypeError):
                category = None
        
        txn.transaction_type = form_data['transaction_type']
        txn.amount = form_data['amount']
        txn.description = form_data['description']
        txn.category = category
        txn.date = form_data['date']
        txn.payment_method = form_data['payment_method']
        txn.note = form_data.get('note', '')
        txn.savings_goal = form_data.get('savings_goal') or None
        txn.save()

        cls._adjust_goal_balance(txn, old_type, old_amount, old_goal)
        return txn

    @classmethod
    @transaction.atomic
    def delete_transaction(cls, txn_id, user):
        """Delete a transaction and atomically revert its contribution to a linked savings goal.
        
        Args:
            txn_id: Primary key of the transaction to delete.
            user: Authenticated user owning the transaction.
            
        Raises:
            ValueError: If the goal balance update fails due to ownership mismatch.
        """
        from django.db.models import F
        from saving_goals.models import SavingGoal
        from .models import Transaction

        txn = Transaction.objects.select_related('savings_goal').get(id=txn_id, user=user)

        if txn.transaction_type == 'income' and txn.savings_goal_id:
            goal_id = txn.savings_goal_id
            updated_rows = SavingGoal.objects.filter(id=goal_id, user=user).update(
                current_amount=F('current_amount') - txn.amount
            )
            if updated_rows == 0:
                raise ValueError("Goal update failed: ID or user mismatch.")

        txn.delete()

    @classmethod
    def get_dashboard_stats(cls, user):
        """Calculate real-time balance, total income, and total expenses for a user.
        
        Args:
            user: Authenticated CustomUser instance.
            
        Returns:
            dict: Dictionary containing 'balance', 'total_income', and 'total_expense'.
        """
        stats = Transaction.objects.filter(user=user).aggregate(
            total_income=Sum('amount', filter=Q(transaction_type='income')),
            total_expense=Sum('amount', filter=Q(transaction_type='expense'))
        )
        total_income = stats['total_income'] or 0
        total_expense = stats['total_expense'] or 0
        return {
            'balance': total_income - total_expense,
            'total_income': total_income,
            'total_expense': total_expense
        }

    @classmethod
    def get_recent_transactions(cls, user, limit=10):
        """Fetch the most recent transactions for dashboard display.
        
        Args:
            user: Authenticated CustomUser instance.
            limit: Maximum number of transactions to return (default: 10).
            
        Returns:
            QuerySet: Ordered Transaction queryset with pre-fetched categories.
        """
        return Transaction.objects.filter(user=user) \
            .select_related('category') \
            .order_by('-date')[:limit]

    @classmethod
    def get_expense_by_category(cls, user, limit=8):
        """Aggregate expenses by category for reporting/pie charts.
        
        Args:
            user: Authenticated CustomUser instance.
            limit: Maximum number of categories to return (default: 8).
            
        Returns:
            list[dict]: List of dictionaries with 'category__name' and 'total' keys.
        """
        return list(
            Transaction.objects
            .filter(user=user, transaction_type='expense')
            .exclude(category=None)
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')[:limit]
        )

    @classmethod
    def get_monthly_income_vs_expense(cls, user, months=6):
        """Calculate monthly income vs expense aggregates for the last N months.
        
        Args:
            user: Authenticated CustomUser instance.
            months: Number of trailing months to calculate (default: 6).
            
        Returns:
            list[dict]: List of dictionaries with 'label', 'income', and 'expense' keys.
        """
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        result = []

        for i in range(months - 1, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

            agg = Transaction.objects.filter(
                user=user,
                date__date__gte=month_start,
                date__date__lte=month_end,
            ).aggregate(
                income=Sum('amount', filter=Q(transaction_type='income')),
                expense=Sum('amount', filter=Q(transaction_type='expense')),
            )

            result.append({
                'label':   month_start.strftime('%b %Y'),
                'income':  float(agg['income']  or 0),
                'expense': float(agg['expense'] or 0),
            })

        return result

    @classmethod
    def _adjust_goal_balance(cls, txn, old_type, old_amount, old_goal):
        """Internal helper to recalculate savings goal balances after transaction updates.
        
        Args:
            txn: Updated Transaction instance.
            old_type: Previous transaction_type value.
            old_amount: Previous amount value.
            old_goal: Previous savings_goal instance.
        """
        if old_type == 'income' and old_goal and old_goal.user == txn.user:
            old_goal.current_amount -= old_amount
            old_goal.save(update_fields=['current_amount'])
        
        if txn.transaction_type == 'income' and txn.savings_goal and txn.savings_goal.user == txn.user:
            txn.savings_goal.current_amount += txn.amount
            txn.savings_goal.save(update_fields=['current_amount'])