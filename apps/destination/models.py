from django.db import models
from base import interface
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.auth.models import User
from apps.media.models import Media


# Create your models here.


class Address(interface.BaseModel):
    address_components = ArrayField(JSONField(blank=True, null=True), blank=True, null=True)
    geometry = JSONField(blank=True, null=True)
    formatted_address = models.CharField(max_length=120, blank=True, null=True)
    place_id = models.CharField(max_length=200, null=True, blank=True, unique=True)
    types = ArrayField(models.CharField(max_length=200), null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.formatted_address


class SearchAddress(interface.BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="searches")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='searches')
    search_keyword = models.CharField(max_length=200, null=True, blank=True)
    tracking_ip = models.CharField(max_length=50, null=True, blank=True)
    count = models.IntegerField(default=1)

    def __str__(self):
        return self.search_keyword


class Destination(interface.BaseModel, interface.Taxonomy):
    title = models.CharField(max_length=120)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="destinations")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='destinations')
    photos = models.ManyToManyField(Media, blank=True, related_name='destinations')
    contact = JSONField(null=True, blank=True)

    def __str__(self):
        return self.title
