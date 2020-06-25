from django.db import models
from base import interface
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.auth.models import User
from apps.media.models import Media
from apps.general.models import Taxonomy


# Create your models here.


class Address(interface.BaseModel):
    address_components = ArrayField(JSONField(blank=True, null=True), blank=True, null=True)
    geometry = JSONField(blank=True, null=True)
    formatted_address = models.CharField(max_length=250, blank=True, null=True)
    place_id = models.CharField(max_length=250, null=True, blank=True, unique=True)
    types = ArrayField(models.CharField(max_length=250), null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.formatted_address


class SearchAddress(interface.BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="searches")
    search_keyword = models.CharField(max_length=200, null=True, blank=True)
    count = models.IntegerField(default=1)
    addresses = models.ManyToManyField(Address, blank=True, related_name='searches')

    def __str__(self):
        return self.search_keyword


class Destination(interface.BaseModel, interface.Taxonomy):
    title = models.CharField(max_length=120)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="destinations")
    parent_destination = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='destinations')
    medias = models.ManyToManyField(Media, blank=True, related_name='destinations')
    contact = JSONField(null=True, blank=True)
    flags = ArrayField(models.CharField(max_length=50, null=True, blank=True), null=True, blank=True)
    taxonomies = models.ManyToManyField(Taxonomy, related_name="destinations", blank=True)

    level = models.IntegerField(default=0)
    process = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id) + ": " + self.title

    def get_all_children(self):
        children = [self]
        try:
            child_list = self.children.all()
        except AttributeError:
            return children
        for child in child_list:
            children.extend(child.get_all_children())
        return children


class DAR(interface.BaseModel):
    destination = models.ForeignKey(Destination, related_name='dars', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    time = models.DateField()

    def __str__(self):
        return str(self.time) + ": " + self.destination.title


class DestinationContribution(interface.BaseModel):
    user = models.ForeignKey(User, related_name='destination_contributions', on_delete=models.CASCADE)
    data = JSONField()
    destination = models.ForeignKey(Destination, related_name='destination_contributions', on_delete=models.CASCADE)
