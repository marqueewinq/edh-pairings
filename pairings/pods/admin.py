from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget
from pods.models import PlayerName, Tournament


class TournamentAdmin(admin.ModelAdmin):
    raw_id_fields = ("players", "owner")
    formfield_overrides = {
        fields.JSONField: {
            "widget": JSONEditorWidget(options={"mode": "form"}, height=60)
        },  # if django < 3.1
        # models.JSONField: {"widget": JSONEditorWidget},
    }


class PlayerNameAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(PlayerName, PlayerNameAdmin)
