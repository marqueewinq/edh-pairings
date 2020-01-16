from django.db import models
from django.contrib.postgres.fields import JSONField


class Tournament(models.Model):
    name = models.CharField(max_length=500, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    data = JSONField(blank=True, null=True)
