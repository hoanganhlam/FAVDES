from django.db import models
from base.interface import BaseModel
import os
import datetime
from uuid import uuid4
from django.core.exceptions import ValidationError
from sorl.thumbnail import ImageField
from django.contrib.auth.models import User


# Create your models here.

def validate_file_size(value):
    file_size = value.size

    if file_size > 10485760:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value


def re_path(instance, filename, bucket):
    now = datetime.datetime.now()
    upload_to = '{}/guess/{}/'.format(bucket, str(now.year) + str(now.month) + str(now.day))
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join(upload_to, filename)


def path_and_rename(instance, filename):
    return re_path(instance, filename, 'favdes/images')


class Media(BaseModel):
    title = models.CharField(max_length=120, blank=True)
    description = models.CharField(max_length=200, blank=True)
    path = ImageField(upload_to=path_and_rename, max_length=500, validators=[validate_file_size])
    user = models.ForeignKey(User, related_name='medias', on_delete=models.SET_NULL, blank=True, null=True)
    is_avatar = models.BooleanField(default=False)
