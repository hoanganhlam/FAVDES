from django.db import models
from base.interface import BaseModel
from apps.media.models import Media
from apps.destination.models import Address
from django.contrib.postgres.fields import JSONField, ArrayField


# Create your models here.


class Worker(BaseModel):
    pass


class IGUser(BaseModel):
    instagram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)


class IGPost(BaseModel):
    instagram_id = models.BigIntegerField(unique=True)
    tags = ArrayField(models.CharField(max_length=100, null=True, blank=True), null=True, blank=True)
    user = models.ForeignKey(IGUser, null=True, blank=True, on_delete=models.SET_NULL, related_name="posts")
    caption = models.TextField(null=True, blank=True, max_length=500)
    time_posted = models.DateTimeField(null=True, blank=True)
    photos = models.ManyToManyField(Media, related_name="ig_posts")
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    coordinate = JSONField(blank=True, null=True)
    photo_types = ArrayField(models.CharField(max_length=100, null=True, blank=True), null=True, blank=True)


class PXUser(BaseModel):
    full_name = models.CharField(max_length=160, blank=True, null=True)
    username = models.CharField(max_length=160)


class PXPost(BaseModel):
    path = models.CharField(max_length=260, blank=True, null=True)
    location_text = models.CharField(max_length=260, blank=True, null=True)
    user = models.ForeignKey(PXUser, on_delete=models.SET_NULL, null=True, blank=True)
