# Generated by Django 2.2.9 on 2020-01-01 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0003_auto_20200101_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
