from django.apps import AppConfig


class CustomerportalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customerportal"

    def ready(self):
        from . import signals
