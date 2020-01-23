from rest_framework import views
from rest_framework import permissions
from rest_framework import generics
from rest_framework.response import Response
from pods.serializers import (
    TournamentSerializer,
    PlayerNameSerializer,
    AddPlayerToTournamentSerializer,
    SubmitResultsTournamentSerializer,
)
from pods.models import Tournament, PlayerName
from pods.judge import new_round, player_set_all_buys, drop_player_from_tournament


class TournamentListCreateView(generics.ListCreateAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Tournament.objects.all().order_by("-date_created")


class TournamentGetUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "id"

    def get_queryset(self):
        return Tournament.objects.all()


class PlayerNameListCreateView(generics.ListCreateAPIView):
    serializer_class = PlayerNameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return PlayerName.objects.all().order_by("-date_created")


class PlayerNameGetUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlayerNameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "id"

    def get_queryset(self):
        return PlayerName.objects.all()


class AddPlayerNameToTournament(views.APIView):
    serializer_class = AddPlayerToTournamentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, id):
        tournament = Tournament.objects.filter(id=id).first()
        if tournament is None:
            return Response({"error": f"ID {id} not found"}, status=404)
        sz = self.serializer_class(data=request.data)
        if sz.is_valid():
            player_name = sz.save()
            tournament.players.add(player_name)
            tournament.data = player_set_all_buys(tournament.data, player_name.name)
            tournament.save()
            return Response({}, status=201)
        return Response(sz.errors, status=400)

    def delete(self, request, id):
        tournament = Tournament.objects.filter(id=id).first()
        if tournament is None:
            return Response({"error": f"ID {id} not found"}, status=404)
        sz = self.serializer_class(data=request.data)
        if sz.is_valid():
            player_name = sz.save()
            tournament.players.remove(player_name)
            return Response({}, status=204)
        return Response(sz.errors, status=400)


class NewRoundInTournament(views.APIView):
    def post(self, request, id):
        tournament = Tournament.objects.filter(id=id).first()
        if tournament is None:
            return Response({"error": f"ID {id} not found"}, status=404)
        tournament.data = new_round(
            tournament.data,
            [
                player_name["name"]
                for player_name in PlayerName.objects.filter(
                    tournament=tournament
                ).values("name")
            ],
        )
        tournament.save()
        return Response(TournamentSerializer(tournament).data, status=201)

class RedoLastRoundInTournament(views.APIView):
    def post(self, request, id):
        tournament = Tournament.objects.filter(id=id).first()
        if tournament is None:
            return Response({"error": f"ID {id} not found"}, status=404)
        if len(tournament.data) > 1:
            tournament.data = tournament.data[:-1]
        else:
            tournament.data = None
        tournament.data = new_round(
            tournament.data,
            [
                player_name["name"]
                for player_name in PlayerName.objects.filter(
                    tournament=tournament
                ).values("name")
            ],
        )
        tournament.save()
        return Response(TournamentSerializer(tournament).data, status=201)

class SubmitResultsTournament(views.APIView):
    serializer_class = SubmitResultsTournamentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, id):
        tournament = Tournament.objects.filter(id=id).first()
        if tournament is None:
            return Response({"error": f"ID {id} not found"}, status=404)
        sz = self.serializer_class(data=request.data)
        if sz.is_valid():
            sz.save()
            return Response({}, status=201)
        return Response(sz.errors, status=400)

class DropPlayerNameFromTournament(views.APIView):
    serializer_class = AddPlayerToTournamentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, id):
        tournament = Tournament.objects.filter(id=id).first()
        if tournament is None:
            return Response({"error": f"ID {id} not found"}, status=404)
        sz = self.serializer_class(data=request.data)
        if sz.is_valid():
            player_name = sz.save()
            tournament.data = drop_player_from_tournament(tournament.data, player_name.name)
            tournament.save()
            return Response({}, status=204)
        return Response(sz.errors, status=400)