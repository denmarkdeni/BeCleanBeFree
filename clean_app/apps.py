from django.apps import AppConfig


class CleanAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clean_app'

    def ready(self):
        import clean_app.signals