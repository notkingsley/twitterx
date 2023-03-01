from django.apps import AppConfig

from . import signals


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self) -> None:
        signals.register_all()