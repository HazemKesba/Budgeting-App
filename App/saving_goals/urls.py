"""
URL routing configuration for the saving_goals application.
Maps browser requests to specific View classes.
"""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.SavingGoalListView.as_view(),name="saving-goals-list"),
    path("create/",views.SavingGoalCreateView.as_view(),  name="saving-goals-create"),
    path("<int:goal_id>/",views.SavingGoalDetailView.as_view(),  name="saving-goals-detail"),
    path("<int:goal_id>/edit/",views.SavingGoalEditView.as_view(),name="saving-goals-edit"),
    path("<int:goal_id>/delete/",views.SavingGoalDeleteView.as_view(),name="saving-goals-delete"),
    path("<int:goal_id>/contribute/",views.GoalContributionView.as_view(),name="goal-contribute"),
]