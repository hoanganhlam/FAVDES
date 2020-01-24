from apps.activity.models import Post, Activity, Follow
from django.contrib import admin

# Register your models here.

admin.site.register((Post, Activity, Follow))
