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
        category = form_data.get('category')
        if form_data.get('new_category_name'):
            category, _ = Category.objects.get_or_create(
                name=form_data['new_category_name'],
                user=user
            )
        
        # 2️⃣ Convert savings_goal ID (string) → SavingsGoal instance
        savings_goal = None
        goal_id = form_data.get('savings_goal')
        if goal_id and goal_id != '':  # Form returns empty string if not selected
            try:
                # 🔒 Security: ensure goal belongs to this user
                savings_goal = SavingGoal.objects.get(id=goal_id, user=user)
            except SavingGoal.DoesNotExist:
                # Silently ignore invalid goal IDs (form validation should catch this)
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
            savings_goal=savings_goal  # ✅ Now passing instance, not string
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
        txn = Transaction.objects.get(id=txn_id, user=user)  # Security: user must own txn
        
        old_amount = txn.amount
        old_goal = txn.savings_goal
        old_type = txn.transaction_type
        
        # Handle new category if requested
        category = form_data.get('category')
        if form_data.get('new_category_name'):
            category, _ = Category.objects.get_or_create(
                name=form_data['new_category_name'],
                user=user
            )
        
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

        # 1️⃣ Fetch transaction + cache the goal relation
        txn = Transaction.objects.select_related('savings_goal').get(id=txn_id, user=user)
        
        print(f"🗑️  Deleting Txn ID: {txn.id} | Type: {txn.transaction_type} | Amount: {txn.amount} | Goal ID: {txn.savings_goal_id}")

        # 2️⃣ Revert goal balance atomically
        if txn.transaction_type == 'income' and txn.savings_goal_id:
            goal_id = txn.savings_goal_id
            print(f"🔄 Reverting Goal {goal_id} by {txn.amount}...")

            updated_rows = SavingGoal.objects.filter(id=goal_id, user=user).update(
                current_amount=F('current_amount') - txn.amount
            )

            print(f"✅ DB updated {updated_rows} row(s)")
            if updated_rows == 0:
                raise ValueError("Goal update failed: ID or user mismatch.")

        # 3️⃣ Delete transaction
        txn.delete()
        print("✅ Transaction deleted. Transaction will commit if no errors follow.")

    @classmethod
    def get_dashboard_stats(cls, user):
        """Calculate balance, income, expense in 1 optimized query"""
        stats = Transaction.objects.filter(user=user).aggregate(
            total_income=Sum('amount', filter=Q(transaction_type='income')),
            total_expense=Sum('amount', filter=Q(transaction_type='expense'))
        )
        
        total_income = stats['total_income'] or 0
        total_expense = stats['total_expense'] or 0
        balance = total_income - total_expense
        
        return {
            'balance': balance,
            'total_income': total_income,
            'total_expense': total_expense
        }
    
    @classmethod
    def get_recent_transactions(cls, user, limit=10):
        return Transaction.objects.filter(user=user) \
            .select_related('category') \
            .order_by('-date')[:limit]

    @classmethod
    def _adjust_goal_balance(cls, txn, old_type, old_amount, old_goal):
        """Helper: recalculate goal balance after transaction update"""
        # Remove old contribution if existed
        if old_type == 'income' and old_goal and old_goal.user == txn.user:
            old_goal.current_amount -= old_amount
            old_goal.save(update_fields=['current_amount'])
        
        # Add new contribution if applicable
        if txn.transaction_type == 'income' and txn.savings_goal and txn.savings_goal.user == txn.user:
            txn.savings_goal.current_amount += txn.amount
            txn.savings_goal.save(update_fields=['current_amount'])