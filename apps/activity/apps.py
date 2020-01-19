from django.apps import AppConfig
from apps.activity.signals import action


class ActivityConfig(AppConfig):
    name = 'apps.activity'

    def ready(self):
        from apps.activity.actions import action_handler
        action.connect(action_handler, dispatch_uid='apps.activity.models')
        from apps.activity import registry
        from apps.activity.models import Post, Activity, Comment
        from apps.destination.models import Destination, Address
        registry.register(Post, Activity, Comment, Destination, Address)
