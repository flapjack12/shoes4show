from django.apps import AppConfig


class Shoes4ShowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "shoes4show"

    def ready(self):
        import shoes4show.signals
