from django.db import models
from base import interface
from django.contrib.auth.models import User
from apps.media.models import Media
from apps.destination.models import Address, DAR, Destination
from apps.general.models import Taxonomy
from apps.activity.managers import ActionManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

# Create your models here.
now = timezone.now


class Post(interface.BaseModel):
    title = models.CharField(max_length=120, null=True, blank=True)
    user = models.ForeignKey(User, related_name="posts", on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(max_length=1000, null=True, blank=True)
    medias = models.ManyToManyField(Media, blank=True, related_name='posts')
    taxonomies = models.ManyToManyField(Taxonomy, blank=True, related_name='posts')
    source = JSONField(null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    date_published = models.DateTimeField(default=timezone.now)
    # POSTED / PENDING / DELETED
    publish_status = models.CharField(max_length=20, default="POSTED")


@python_2_unicode_compatible
class Activity(interface.BaseModel):
    verb = models.CharField(max_length=255, db_index=True)

    actor_content_type = models.ForeignKey(
        ContentType, related_name='actor',
        on_delete=models.CASCADE, db_index=True
    )
    actor_object_id = models.CharField(max_length=255, db_index=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        related_name='action_object',
        on_delete=models.CASCADE, db_index=True
    )
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    target_content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        related_name='target',
        on_delete=models.CASCADE, db_index=True
    )

    target_object_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='activities')

    voters = models.ManyToManyField(User, blank=True, related_name='voted_activities')
    tagged = models.ManyToManyField(User, blank=True, related_name='tagged_activities')
    objects = ActionManager()

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'created': self.created
        }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(created)s ago') % ctx
            return _('%(actor)s %(verb)s %(target)s %(created)s ago') % ctx
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(created)s ago') % ctx
        return _('%(actor)s %(verb)s %(created)s ago') % ctx

    def make_dar(self):
        if self.address:
            for destination in self.address.destinations.filter(flags__contains=["SPECIAL"]):
                test = DAR.objects.filter(time=self.created, destination=destination).first()
                if test is None:
                    children = destination.get_all_children()
                    address_ids = list(map(lambda x: x.address.pk, children))
                    count = Activity.objects.filter(address__id__in=address_ids, created__day=self.created.day,
                                                    created__month=self.created.month,
                                                    created__year=self.created.year).count()
                    test = DAR(time=self.created, destination=destination, count=count)
                else:
                    test.count = test.count + 1
                test.save()


class Comment(interface.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=500)
    voters = models.ManyToManyField(User, blank=True, related_name='voted_comments')


@python_2_unicode_compatible
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_id = models.CharField(max_length=255, db_index=True)
    follow_object = GenericForeignKey()

    actor_only = models.BooleanField(
        "Only follow actions where "
        "the object is the target.",
        default=True
    )

    is_pending = models.BooleanField(default=False)
    flag = models.CharField(max_length=255, blank=True, db_index=True, default='')
    started = models.DateTimeField(default=now, db_index=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id', 'flag')

    def __str__(self):
        return '%s -> %s : %s' % (self.user, self.follow_object, self.flag)
