from django.apps import AppConfig


class WorkerConfig(AppConfig):
    name = 'apps.worker'

    def ready(self):
        from apps.worker import signals
