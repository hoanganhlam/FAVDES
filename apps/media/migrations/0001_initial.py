# Generated by Django 3.0 on 2019-12-22 03:44

import apps.media.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(blank=True, max_length=120)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('path', models.ImageField(max_length=500, upload_to=apps.media.models.path_and_rename, validators=[apps.media.models.validate_file_size])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]