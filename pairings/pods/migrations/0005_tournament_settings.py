# Generated by Django 2.2.28 on 2023-01-20 09:16

import django.contrib.postgres.fields.jsonb
import pods.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pods", "0004_auto_20230116_1217"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="settings",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=pods.models.make_default_tournament_settings,
                null=True,
            ),
        ),
    ]
