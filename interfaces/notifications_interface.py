from abc import ABC, abstractmethod


class NotificationsInterface(ABC):
    @abstractmethod
    def send_notifications(self, message: str):
        pass
