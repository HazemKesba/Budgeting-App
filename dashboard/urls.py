"""URL routing for the dashboard application."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
]