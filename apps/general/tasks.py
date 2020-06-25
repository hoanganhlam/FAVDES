from apps.activity.models import Post
from django.utils import timezone
from apps.activity import action
from django.contrib.auth.models import User


def my_cron_job():
    lam = User.objects.get(pk=1)
    if lam.profile.options is None:
        lam.profile.options = {}
    is_running = lam.profile.options.get("cron_running", False)
    if not is_running:
        lam.profile.options["cron_running"] = True
        lam.profile.save()
        posts = Post.objects.filter(publish_status="PENDING", date_published__lte=timezone.now())
        for post in posts:
            action.send(
                sender=post.user,
                verb='POSTED',
                action_object=post,
                address=post.address,
                destination=post.destination
            )
            post.publish_status = "POSTED"
            post.save()
        lam.profile.options["cron_running"] = False
        lam.profile.save()
