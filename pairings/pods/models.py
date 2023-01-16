from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from rest_framework.authtoken.models import Token


class PlayerName(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    STATUS_NEW, STATUS_STARTED, STATUS_FINISHED = range(3)
    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_STARTED, "Started"),
        (STATUS_FINISHED, "Finished"),
    )

    name = models.CharField(max_length=500, null=True)
    date_created = models.DateTimeField(default=now)
    date_updated = models.DateTimeField(auto_now=True)

    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_NEW)
    players = models.ManyToManyField(PlayerName)
    data = JSONField(blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} at {self.date_created}"


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Create Token object, when User object create
    token is used as Token.key
    :param sender:
    :param instance: User instance
    :param created: True if User object created
    :param kwargs:
    :return:
    """
    if created:
        Token.objects.create(user=instance)
