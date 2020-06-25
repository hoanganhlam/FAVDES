from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from apps.media.models import Media


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    nick = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    media = models.ForeignKey(Media, related_name='profile', on_delete=models.SET_NULL, null=True, blank=True)
    social = JSONField(blank=True, null=True)
    options = JSONField(blank=True, null=True)
    source = JSONField(null=True, blank=True)
