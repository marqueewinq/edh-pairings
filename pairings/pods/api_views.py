from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from pods.serializers import TournamentSerializer, AddPlayerToTournamentSerializer
from pods.models import Tournament


class TournamentListCreateView(ListCreateAPIView):
    serializer_class = TournamentSerializer

    def get_queryset(self):
        return Tournament.objects.all().order_by("-date_created")


class TournamentGetUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = TournamentSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Tournament.objects.all()


class AddPlayerNameToTournament(APIView):
    serializer_class = AddPlayerToTournamentSerializer

    def post(self, request, id):
        tournament = Tournament.objects.filter(id = id).first()
        if tournament is None:
            return Response({"error": f"ID {id} not found"}, status=404)
        sz = self.serializer_class(data=request.data)
        if sz.is_valid():
            instance = sz.save()
            tournament.players.add(instance)
            return Response({}, status=200)
        return Response(sz.errors, status=400)
