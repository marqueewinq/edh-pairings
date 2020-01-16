from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    ListAPIView,
    DestroyAPIView,
)
from pods.serializers import TournamentSerializer


class TournamentListCreateView(RetrieveUpdateDestroyAPIView):
    serializer_class = TournamentSerializer
