from pods import viewsets
from rest_framework import routers

api_v1_router = routers.SimpleRouter()
api_v1_router.register(r"api/v1/players", viewsets.PlayerNameViewSet)
api_v1_router.register(r"api/v1/tournaments", viewsets.TournamentViewSet)

urlpatterns = api_v1_router.urls
