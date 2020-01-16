from django.urls import path

from pods import views
from pods import api_views


# fmt: off
urlpatterns = [
    # Served views
    path('', views.index, name='index'),
    # API
    path('api/v1/tournaments/', api_views.TournamentListCreateView.as_view(), "api_tournaments")
]
# fmt: on
