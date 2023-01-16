# Generated by Django 2.2.28 on 2023-01-16 13:19

import uuid

import django.utils.timezone
import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="NewsEntry",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("html_entry", tinymce.models.HTMLField()),
            ],
        ),
    ]
