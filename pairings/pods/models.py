from django.db import models
from django.contrib.postgres.fields import JSONField


class PlayerName(models.Model):
    name = models.CharField(max_length=500)


class Tournament(models.Model):
    STATUS_NEW, STATUS_STARTED, STATUS_FINISHED = range(3)
    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_STARTED, "Started"),
        (STATUS_FINISHED, "Finished"),
    )

    name = models.CharField(max_length=500, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_NEW)
    players = models.ManyToManyField(PlayerName)
    data = JSONField(blank=True, null=True)


