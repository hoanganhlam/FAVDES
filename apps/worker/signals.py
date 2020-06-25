from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.activity import action, actions
from apps.activity.models import Activity, Post
from base.db.redis import rediscontroller
from apps.activity.api.serializers import ActivitySerializer
import json
from apps.activity import verbs

redis = rediscontroller.RedisController()
redis.start()


@receiver(post_save, sender=Activity)
def activity_create(sender, instance, created, **kwargs):
    if created:
        if instance.actor.__class__.__name__ == 'User' and instance.verb != verbs.FOLLOWED:
            if not actions.is_following(instance.actor, obj=instance):
                actions.follow(user=instance.actor, obj=instance)
            if instance.action_object:
                if not actions.is_following(instance.actor, obj=instance.action_object):
                    actions.follow(user=instance.actor, obj=instance.action_object)
        groups = []
        if instance.target:
            group = '{0}_{1}'.format(instance.target.__class__.__name__, instance.target.pk).lower()
            groups.append(group)
        payload = {
            'groups': groups,
            'type': 'notify',
            'data': ActivitySerializer(instance).data
        }
        try:
            redis.notify(json.dumps(payload))
        except Exception as e:
            print(e)
        instance.make_dar()
