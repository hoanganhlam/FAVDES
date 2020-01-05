from django.db import models
from django.contrib.auth.models import User
from apps.media.models import Media


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True, blank=True)
    media = models.ForeignKey(Media, related_name='profile', on_delete=models.SET_NULL, null=True, blank=True)
