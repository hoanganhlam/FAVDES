from django.contrib import admin
from apps.destination.models import Destination, Point, Address, SearchAddress
from apps.authentication.models import Profile

# Register your models here.

admin.site.register((Destination, Point, Address, SearchAddress, Profile))
