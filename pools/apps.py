from django.apps import AppConfig


class PoolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pools'

    def ready(self):
        from pools import signals  # noqa: F401