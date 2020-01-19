from django.contrib import admin
from apps.destination.models import Destination, Address, SearchAddress
from apps.authentication.models import Profile

# Register your models here.

admin.site.register((Destination, Address, SearchAddress, Profile))
