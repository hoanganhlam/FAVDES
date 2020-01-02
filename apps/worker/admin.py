from django.contrib import admin
from apps.worker.models import IGPost, IGUser

# Register your models here.

admin.site.register((IGPost, IGUser))
