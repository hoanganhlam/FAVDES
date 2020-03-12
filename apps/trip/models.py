from django.db import models
from base.interface import BaseModel
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from apps.general.models import Taxonomy
from apps.destination.models import Destination
from apps.media.models import Media

# Create your models here.


class Schedule(BaseModel):
    title = models.CharField(max_length=120, blank=True, null=True)
    slug = models.CharField(max_length=120, blank=True, null=True)
    note = models.TextField(max_length=500, blank=True, null=True)
    destination_start = models.ForeignKey(
        Destination, related_name='start_schedules', on_delete=models.CASCADE, null=True,
        blank=True
    )
    destination_end = models.ForeignKey(
        Destination, related_name='end_schedules', on_delete=models.CASCADE, null=True,
        blank=True
    )
    user = models.ForeignKey(User, related_name="schedules", on_delete=models.CASCADE)
    options = JSONField(null=True, blank=True)
    taxonomies = models.ManyToManyField(Taxonomy, related_name="schedules", blank=True)
    media = models.ForeignKey(Media, related_name="schedules", blank=True, null=True, on_delete=models.SET_NULL)
    privacy = models.CharField(max_length=50, null=True, blank=True)
    allow_users = models.ManyToManyField(User, related_name="allow_view_schedules", blank=True)
    deny_users = models.ManyToManyField(User, related_name="deny_view_schedules", blank=True)


class Role(models.Model):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=120)
    key = models.CharField(max_length=120)


class ScheduleMember(models.Model):
    user = models.ForeignKey(User, related_name="schedule_member", on_delete=models.CASCADE)
    role = models.ForeignKey(Role, related_name="schedule_member", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="PENDING")
    schedule = models.ForeignKey(Schedule, related_name="schedule_member", on_delete=models.CASCADE)


class Task(BaseModel):
    title = models.CharField(max_length=120, unique=True)
    note = models.TextField(max_length=500, blank=True, null=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="tasks")
    user = models.ForeignKey(User, related_name="tasks", on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    options = JSONField(null=True, blank=True)


class Discussion(BaseModel):
    trip = models.ForeignKey(Schedule, related_name='discussions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="trip_discussions", on_delete=models.CASCADE)
    content = models.TextField()
    voters = models.ManyToManyField(User, related_name='discussion_voted', blank=True)
