from abc import ABC, abstractmethod
from django.contrib import messages


class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: dict, request=None):
        pass


class NotificationObserver(Observer):

    def update(self, event: str, data: dict, request=None):
        if request is None:
            return

        if event == "goal_completed":
            messages.success(request, f"Congratulations! Goal '{data['goal_name']}' is completed!")

        elif event == "contribution_added":
            messages.success(request, f"EGP {data['amount']} added to '{data['goal_name']}'. Progress: {data['progress']}%")

        elif event == "goal_created":
            messages.success(request, f"Goal '{data['goal_name']}' created successfully.")


class DashboardUIObserver(Observer):

    def update(self, event: str, data: dict, request=None):
        if request is None:
            return

        if event == "goal_completed":
            messages.info(request, "Your dashboard has been updated with the completed goal.")


class GoalManager:

    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, event: str, data: dict, request=None):
        for observer in self._observers:
            observer.update(event, data, request=request)


goal_manager = GoalManager()
goal_manager.attach(NotificationObserver())
goal_manager.attach(DashboardUIObserver())