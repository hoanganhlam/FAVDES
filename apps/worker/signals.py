from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.activity import action, actions
from apps.activity.models import Activity, Post
from base.db.redis import rediscontroller
from apps.activity.api.serializers import ActivitySerializer
import json
from apps.activity import verbs
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

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


@receiver(post_save, sender=Post)
def post_create(sender, instance, created, **kwargs):
    if not created:
        handle_update(instance)


def handle_update(instance):
    ct = ContentType.objects.get_for_model(instance)
    q = Q(
        target_content_type=ct,
        target_object_id=instance.id
    ) | Q(
        action_object_content_type=ct,
        action_object_object_id=instance.id,
    ) | Q(
        actor_content_type=ct,
        actor_object_id=instance.id
    )
    activities = Activity.objects.filter(q)
    for activity in activities:
        activity.temp = {
            "actor": convert_serializer(activity.actor),
            "action_object": convert_serializer(activity.action_object),
            "target": convert_serializer(activity.target)
        }
        activity.save()
