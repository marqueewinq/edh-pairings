from django.contrib import admin
from pods.models import PlayerName, Tournament


class TournamentAdmin(admin.ModelAdmin):
    pass


class PlayerNameAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(PlayerName, PlayerNameAdmin)
