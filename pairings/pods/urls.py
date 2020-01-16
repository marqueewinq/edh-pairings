from django.urls import path

from pods import views
from pods import api_views


# fmt: off
urlpatterns = [
    # Served views
    path('', views.index, name='index'),
    path('tournaments/<int:id>/', views.detail, name="detail"),
    # API
    path('api/v1/tournaments/', api_views.TournamentListCreateView.as_view(), name="api_tournaments"),
    path('api/v1/tournaments/<int:id>/', api_views.TournamentGetUpdateDeleteView.as_view(), name="api_tournament"),
    path('api/v1/tournaments/<int:id>/add/', api_views.AddPlayerNameToTournament.as_view(), name="api_tournament_add"),

]
# fmt: on
