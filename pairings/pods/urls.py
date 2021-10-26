from django.urls import path, include

from pods import views
from pods import api_views


# fmt: off
urlpatterns = [
    # Served views
    path('', views.index, name='index'),
    path('tournaments/<int:id>/', views.detail, name="detail"),
    # Auth
    path('accounts/', include('rest_auth.urls')),
    # API
    path('api/v1/tournaments/', api_views.TournamentListCreateView.as_view(), name="api_tournaments"),
    path('api/v1/tournaments/<int:id>/', api_views.TournamentGetUpdateDeleteView.as_view(), name="api_tournament"),
    path('api/v1/tournaments/<int:id>/add/', api_views.AddPlayerNameToTournament.as_view(), name="api_tournament_add"),
    path('api/v1/tournaments/<int:id>/drop/', api_views.DropPlayerNameFromTournament.as_view(), name="api_tournament_drop"),
    path('api/v1/tournaments/<int:id>/round/', api_views.NewRoundInTournament.as_view(), name="api_tournament_round"),
    path('api/v1/tournaments/<int:id>/round/redo/', api_views.RedoLastRoundInTournament.as_view(), name="api_tournament_round_redo"),
    path('api/v1/tournaments/<int:id>/submit/', api_views.SubmitResultsTournament.as_view(), name="api_tournament_submit"),
    path('api/v1/players/', api_views.PlayerNameListCreateView.as_view(), name="api_players"),
    path('api/v1/players/<int:id>/', api_views.PlayerNameGetUpdateDeleteView.as_view(), name="api_player"),
]
# fmt: on
