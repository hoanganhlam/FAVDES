# Generated by Django 2.2.9 on 2020-01-01 06:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='description',
        ),
        migrations.AddField(
            model_name='activity',
            name='tagged',
            field=models.ManyToManyField(blank=True, related_name='tagged_activities', to=settings.AUTH_USER_MODEL),
        ),
    ]
