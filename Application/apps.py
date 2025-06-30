from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Application'

    def ready(self):
        from . import signals