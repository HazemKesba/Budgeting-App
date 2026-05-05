from datetime import date
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
from . import services


class SavingGoalListView(LoginRequiredMixin, View):

    def get(self, request):
        status_filter = request.GET.get("status")
        goals = services.get_user_goals(request.user, status_filter=status_filter)
        context = {
            "goals":[services.build_goal_data(g) for g in goals],
            "status_filter": status_filter,
        }
        return render(request, "saving_goals/list.html", context)


class SavingGoalDetailView(LoginRequiredMixin, View):

    def get(self, request, goal_id):
        goal = services.get_goal(request.user, goal_id)
        if goal is None:
            messages.error(request, "Goal not found.")
            return redirect("saving-goals-list")
        return render(request, "saving_goals/detail.html", {"goal": services.build_goal_data(goal)})


class SavingGoalCreateView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "saving_goals/create.html")

    def post(self, request):
        goal_name = request.POST.get("goal_name", "")
        target_amount = request.POST.get("target_amount")
        current_amount = request.POST.get("current_amount", 0)
        deadline_str = request.POST.get("deadline", "")

        try:
            deadline = date.fromisoformat(deadline_str)
        except ValueError:
            messages.error(request, "Invalid deadline format.")
            return render(request, "saving_goals/create.html", {"form_data": request.POST})

        try:
            goal = services.create_goal(
                user=request.user,
                goal_name=goal_name,
                target_amount=target_amount,
                current_amount=current_amount,
                deadline=deadline,
                request=request,
            )
            return redirect("saving-goals-detail", goal_id=goal.id)

        except ValidationError as e:
            messages.error(request, e.message)
            return render(request, "saving_goals/create.html", {"form_data": request.POST})


class SavingGoalEditView(LoginRequiredMixin, View):

    def get(self, request, goal_id):
        goal = services.get_goal(request.user, goal_id)
        if goal is None:
            messages.error(request, "Goal not found.")
            return redirect("saving-goals-list")
        return render(request, "saving_goals/edit.html", {"goal": services.build_goal_data(goal)})

    def post(self, request, goal_id):
        fields = {}

        if request.POST.get("goal_name"):
            fields["goal_name"] = request.POST.get("goal_name")

        if request.POST.get("target_amount"):
            fields["target_amount"] = request.POST.get("target_amount")

        if request.POST.get("deadline"):
            try:
                fields["deadline"] = date.fromisoformat(request.POST.get("deadline"))
            except ValueError:
                messages.error(request, "Invalid deadline format.")
                return redirect("saving-goals-edit", goal_id=goal_id)

        try:
            goal = services.update_goal(request.user, goal_id, **fields)
            if goal is None:
                messages.error(request, "Goal not found.")
                return redirect("saving-goals-list")
            messages.success(request, "Goal updated successfully.")
            return redirect("saving-goals-detail", goal_id=goal.id)

        except ValidationError as e:
            messages.error(request, e.message)
            return redirect("saving-goals-edit", goal_id=goal_id)


class SavingGoalDeleteView(LoginRequiredMixin, View):

    def get(self, request, goal_id):
        goal = services.get_goal(request.user, goal_id)
        if goal is None:
            messages.error(request, "Goal not found.")
            return redirect("saving-goals-list")
        return render(request, "saving_goals/delete_confirm.html", {"goal": services.build_goal_data(goal)})

    def post(self, request, goal_id):
        deleted = services.delete_goal(request.user, goal_id)
        if not deleted:
            messages.error(request, "Goal not found.")
        else:
            messages.success(request, "Goal deleted successfully.")
        return redirect("saving-goals-list")


class GoalContributionView(LoginRequiredMixin, View):

    def post(self, request, goal_id):
        amount = request.POST.get("amount")

        try:
            services.add_contribution(request.user, goal_id, amount, request=request)
        except ValidationError as e:
            messages.error(request, e.message)

        return redirect("saving-goals-detail", goal_id=goal_id)