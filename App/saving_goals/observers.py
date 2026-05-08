"""
Implementation of the Observer Design Pattern for saving goal events.
This module handles decoupling event triggers (like goal completion) 
from their side effects (like notifications or UI updates).
"""
from abc import ABC, abstractmethod
from django.contrib import messages


class Observer(ABC):
    """Abstract Base Class for all observers."""
    @abstractmethod
    def update(self, event: str, data: dict, request=None):
        """
        Update method called by the Subject (GoalManager).
        
        Args:
            event (str): The name of the event triggered.
            data (dict): Contextual data for the event.
            request (HttpRequest, optional): The Django request object for messages.
        """
        pass


class NotificationObserver(Observer):
    """Observer that handles sending user-facing success messages."""

    def update(self, event: str, data: dict, request=None):
        """Triggers Django success messages based on specific goal events."""
        if request is None:
            return

        if event == "goal_completed":
            messages.success(request, f"Congratulations! Goal '{data['goal_name']}' is completed!")

        elif event == "contribution_added":
            messages.success(request, f"EGP {data['amount']} added to '{data['goal_name']}'. Progress: {data['progress']}%")

        elif event == "goal_created":
            messages.success(request, f"Goal '{data['goal_name']}' created successfully.")


class DashboardUIObserver(Observer):
    """Observer that handles UI-specific updates or information messages."""

    def update(self, event: str, data: dict, request=None):
        """Triggers informational messages for dashboard updates."""
        if request is None:
            return

        if event == "goal_completed":
            messages.info(request, "Your dashboard has been updated with the completed goal.")


class GoalManager:
    """
    The Subject in the Observer pattern. 
    Manages a list of observers and notifies them of state changes.
    """

    def __init__(self):
        """Initializes the manager with an empty list of observers."""
        self._observers: list[Observer] = []

    def attach(self, observer: Observer):
        """Registers an observer."""
        self._observers.append(observer)

    def detach(self, observer: Observer):
        """Removes a registered observer."""
        self._observers.remove(observer)

    def notify(self, event: str, data: dict, request=None):
        """Notifies all attached observers of an event."""
        for observer in self._observers:
            observer.update(event, data, request=request)


# Singleton-like instance of the manager, initialized with default observers
goal_manager = GoalManager()
goal_manager.attach(NotificationObserver())
goal_manager.attach(DashboardUIObserver())