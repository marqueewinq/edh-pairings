import uuid

from django.db import models
from django.utils.timezone import now
from tinymce.models import HTMLField


class NewsEntry(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)

    date_created = models.DateTimeField(default=now)
    html_entry = HTMLField()
    html_entry_ru = HTMLField(default="")

    def __str__(self):
        return f"{self.date_created} {self.uuid}"
