from interfaces.notifications_interface import NotificationsInterface


class ConsoleNotificationStrategy(NotificationsInterface):
    def send_notifications(self, message: str):
        print(message)
