from apps.activity.models import Post, Activity, Follow, Taxonomy
from django.contrib import admin

# Register your models here.

admin.site.register((Post, Activity, Follow, Taxonomy))
