from django.db import models
from django_extensions.db.fields import AutoSlugField


class ClanCollection(models.Model):
    platform_id = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='name', unique=True)
    owner = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
