from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from pods.models import PlayerName, Tournament


class TournamentAdmin(admin.ModelAdmin):
    raw_id_fields = ("players", "owner")
    formfield_overrides = {
        models.JSONField: {
            "widget": JSONEditorWidget(options={"mode": "form"}, height=60)
        },
    }


class PlayerNameAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(PlayerName, PlayerNameAdmin)
