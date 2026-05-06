from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import Transaction, Category
from django.db.models import F, Q, Sum

class TransactionService:
    @classmethod
    @transaction.atomic
    def create_transaction(cls, user, form_data: dict):
        """
        Create transaction + optionally update linked savings goal.
        form_ cleaned_data from TransactionForm (plain Form)
        """
        from saving_goals.models import SavingGoal
        
        # 1️⃣ Handle new category creation if requested
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
        
        # 2️⃣ Convert savings_goal ID (string) → SavingsGoal instance
        savings_goal = None
        goal_id = form_data.get('savings_goal')
        if goal_id and goal_id != '':
            try:
                savings_goal = SavingGoal.objects.get(id=goal_id, user=user)
            except SavingGoal.DoesNotExist:
                pass
        
        # 3️⃣ Create the transaction
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

        # 4️⃣ If income + linked to goal → update goal balance
        if txn.transaction_type == 'income' and txn.savings_goal:
            goal = txn.savings_goal
            goal.current_amount += txn.amount
            goal.save(update_fields=['current_amount'])

        return txn

    @classmethod
    @transaction.atomic
    def update_transaction(cls, txn_id, user, form_data: dict):
        """Update transaction + adjust goal balance if needed"""
        txn = Transaction.objects.get(id=txn_id, user=user)
        
        old_amount = txn.amount
        old_goal = txn.savings_goal
        old_type = txn.transaction_type
        
        # Handle new category if requested
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
        
        # Update basic fields
        txn.transaction_type = form_data['transaction_type']
        txn.amount = form_data['amount']
        txn.description = form_data['description']
        txn.category = category
        txn.date = form_data['date']
        txn.payment_method = form_data['payment_method']
        txn.note = form_data.get('note', '')
        txn.savings_goal = form_data.get('savings_goal') or None
        txn.save()

        # 🔄 Adjust goal balance if income linkage changed
        cls._adjust_goal_balance(txn, old_type, old_amount, old_goal)
        return txn

    @classmethod
    @transaction.atomic
    def delete_transaction(cls, txn_id, user):
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
        """Calculate balance, income, expense in 1 optimized query"""
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
        return Transaction.objects.filter(user=user) \
            .select_related('category') \
            .order_by('-date')[:limit]

    @classmethod
    def get_expense_by_category(cls, user, limit=8):
        """
        Return a list of dicts {category__name, total} for the user's expenses,
        grouped by category, ordered by total descending.
        Used by the dashboard pie chart.
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
        """
        Return a list of dicts for the last `months` calendar months:
          {label: 'Jan 2025', income: Decimal, expense: Decimal}
        Used by the dashboard bar chart.
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
        """Helper: recalculate goal balance after transaction update"""
        if old_type == 'income' and old_goal and old_goal.user == txn.user:
            old_goal.current_amount -= old_amount
            old_goal.save(update_fields=['current_amount'])
        
        if txn.transaction_type == 'income' and txn.savings_goal and txn.savings_goal.user == txn.user:
            txn.savings_goal.current_amount += txn.amount
            txn.savings_goal.save(update_fields=['current_amount'])