from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import SavingGoal
from .observers import goal_manager
from .singleton import SessionManager


def create_goal(user, goal_name, target_amount, deadline, current_amount=0, request=None):
    if not goal_name or not goal_name.strip():
        raise ValidationError("Goal name is required.")

    target_amount  = Decimal(str(target_amount))
    current_amount = Decimal(str(current_amount))

    if target_amount <= 0:
        raise ValidationError("Target amount must be greater than 0.")

    if current_amount < 0:
        raise ValidationError("Current amount cannot be negative.")

    if current_amount > target_amount:
        raise ValidationError("Current amount cannot exceed target amount.")

    if deadline <= timezone.now().date():
        raise ValidationError("Deadline must be a future date.")

    status = (
        SavingGoal.Status.COMPLETED
        if current_amount >= target_amount
        else SavingGoal.Status.IN_PROGRESS
    )

    goal = SavingGoal.objects.create(
        user=user,
        goal_name=goal_name.strip(),
        target_amount=target_amount,
        current_amount=current_amount,
        deadline=deadline,
        status=status,
    )

    goal_manager.notify("goal_created", {"goal_name": goal.goal_name}, request=request)
    return goal


def get_user_goals(user, status_filter=None):
    qs = SavingGoal.objects.filter(user=user)
    if status_filter:
        qs = qs.filter(status=status_filter)
    return qs


def get_goal(user, goal_id):
    try:
        return SavingGoal.objects.get(id=goal_id, user=user)
    except SavingGoal.DoesNotExist:
        return None


def update_goal(user, goal_id, **fields):
    goal = get_goal(user, goal_id)
    if goal is None:
        return None

    allowed = {"goal_name", "target_amount", "deadline"}
    for field, value in fields.items():
        if field not in allowed:
            continue

        if field == "goal_name":
            if not value or not value.strip():
                raise ValidationError("Goal name is required.")
            value = value.strip()

        if field == "target_amount":
            value = Decimal(str(value))
            if value <= 0:
                raise ValidationError("Target amount must be greater than 0.")
            if goal.current_amount > value:
                raise ValidationError("Target amount cannot be less than the amount already saved.")

        if field == "deadline":
            if value <= timezone.now().date():
                raise ValidationError("Deadline must be a future date.")

        setattr(goal, field, value)

    goal.save()
    return goal


def delete_goal(user, goal_id):
    goal = get_goal(user, goal_id)
    if goal is None:
        return False
    goal.delete()
    session = SessionManager()
    session.clear()

    return True


def add_contribution(user, goal_id, amount, request=None):
    goal = get_goal(user, goal_id)
    if goal is None:
        return None

    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValidationError("Contribution amount must be greater than 0.")

    if goal.status == SavingGoal.Status.COMPLETED:
        raise ValidationError("This goal is already completed.")

    goal.current_amount = min(goal.target_amount, goal.current_amount + amount)

    if goal.current_amount >= goal.target_amount:
        goal.status = SavingGoal.Status.COMPLETED
        goal.save(update_fields=["current_amount", "status", "updated_at"])
        goal_manager.notify("goal_completed", {"goal_name": goal.goal_name}, request=request)
    else:
        goal.save(update_fields=["current_amount", "updated_at"])
        goal_manager.notify("contribution_added", {
            "goal_name": goal.goal_name,
            "amount":    str(amount),
            "progress":  str(calculate_progress(goal)),
        }, request=request)
    session = SessionManager()
    session.set("last_viewed_goal", goal.id)
    session.set("last_progress", str(calculate_progress(goal)))

    return goal


def calculate_progress(goal):
    if goal.target_amount == 0:
        return Decimal("0.00")
    raw = (goal.current_amount / goal.target_amount) * 100
    return min(Decimal("100.00"), round(raw, 2))


def calculate_monthly_saving_needed(goal):
    today  = timezone.now().date()
    months = (goal.deadline.year - today.year) * 12 + (goal.deadline.month - today.month)
    months = max(1, months)
    remaining = max(Decimal("0.00"), goal.target_amount - goal.current_amount)
    return round(remaining / months, 2)


def build_goal_data(goal):
    session = SessionManager()
    session.set("last_viewed_goal", goal.id)

    return {
        "id": goal.id,
        "goal_name": goal.goal_name,
        "target_amount":str(goal.target_amount),
        "current_amount":str(goal.current_amount),
        "remaining_amount":str(max(Decimal("0.00"), goal.target_amount - goal.current_amount)),
        "deadline":goal.deadline.isoformat(),
        "status":goal.status,
        "progress_percentage":str(calculate_progress(goal)),
        "monthly_saving_needed":str(calculate_monthly_saving_needed(goal)),
        "created_at":goal.created_at.isoformat(),
        "updated_at":goal.updated_at.isoformat(),
    }