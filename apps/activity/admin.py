from apps.activity.models import Post, Activity
from django.contrib import admin

# Register your models here.

admin.site.register((Post, Activity))
