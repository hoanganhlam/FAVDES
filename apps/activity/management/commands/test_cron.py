from django.core.management.base import BaseCommand
from apps.activity.models import Post
from django.utils import timezone
from apps.activity import action


class Command(BaseCommand):
    def handle(self, *args, **options):
        posts = Post.objects.filter(date_published__lte=timezone.now())
        for post in posts:
            action.send(
                sender=post.user,
                verb='POSTED',
                action_object=post,
                address=post.address,
                destination=post.destination
            )
