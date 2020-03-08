from django.db import models
from base import interface


# Create your models here.

class Taxonomy(interface.Taxonomy, interface.BaseModel):
    flag = models.CharField(max_length=50, default="NORMAL")
