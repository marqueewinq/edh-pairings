from django.db import transaction
from judge import Judge
from pods.exceptions import PlayerNameNotInTournamentError
from pods.models import PlayerName, Tournament
from pods.permissions import IsTournamentOwnerOrReadOnly
from pods.serializers import (
    AddPlayerToTournamentSerializer,
    PlayerNameSerializer,
    SubmitResultsTournamentSerializer,
    TournamentSerializer,
)
from rest_framework import decorators, exceptions, permissions, status, viewsets
from rest_framework.response import Response


class PlayerNameViewSet(viewsets.ModelViewSet):
    queryset = PlayerName.objects.all().order_by("-date_created")
    serializer_class = PlayerNameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "id"


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all().order_by("-date_created", "-id")
    serializer_class = TournamentSerializer
    permission_classes = [
        IsTournamentOwnerOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    ]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        url_path="add",
        serializer_class=AddPlayerToTournamentSerializer,
    )
    def add_player_to_tournament(self, request, id=None):
        tournament = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.method == "POST":
            return self._add_player_to_tournament(serializer, tournament)
        elif request.method == "DELETE":
            return self._remove_player_from_tournament(serializer, tournament)
        raise exceptions.MethodNotAllowed(method=request.method)

    @decorators.action(
        detail=True,
        methods=["post"],
        url_path="drop",
        serializer_class=AddPlayerToTournamentSerializer,
    )
    def drop_player_from_tournament(self, request, id=None):
        tournament = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self._drop_player_from_tournament(serializer, tournament)

    @staticmethod
    @transaction.atomic
    def _add_player_to_tournament(serializer, tournament):
        player_name = serializer.save()
        tournament.players.add(player_name)
        tournament.data = Judge(config=tournament.judge_config).player_set_all_buys(
            tournament.data, player_name.name
        )
        tournament.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    @transaction.atomic
    def _remove_player_from_tournament(serializer, tournament):
        player_name = serializer.save()
        tournament.players.remove(player_name)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    @transaction.atomic
    def _drop_player_from_tournament(serializer, tournament):
        player_name = serializer.save()
        if not tournament.players.filter(id=player_name.id).exists():
            raise PlayerNameNotInTournamentError(player_name.name)
        tournament.data = Judge(
            config=tournament.judge_config
        ).drop_player_from_tournament(tournament.data, player_name.name)
        tournament.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=True,
        methods=["post"],
        url_path="round",
    )
    def create_new_round_in_tournament(self, request, id=None):
        tournament = self.get_object()
        tournament.data = Judge(config=tournament.judge_config).new_round(
            tournament.data,
            [
                player_name["name"]
                for player_name in PlayerName.objects.filter(
                    tournament=tournament
                ).values("name")
            ],
        )
        tournament.save()
        return Response(self.get_serializer(tournament).data, status=status.HTTP_200_OK)

    @decorators.action(
        detail=True,
        methods=["post"],
        url_path="round/redo",
    )
    def redo_last_round_in_tournament(self, request, id=None):
        tournament = self.get_object()
        if tournament.data is None:
            raise exceptions.ValidationError(detail="No rounds in this tournament yet.")
        tournament.data = Judge(config=tournament.judge_config).redo_last_round(
            tournament.data,
            [
                player_name["name"]
                for player_name in PlayerName.objects.filter(
                    tournament=tournament
                ).values("name")
            ],
        )

        tournament.save()
        return Response(self.get_serializer(tournament).data, status=status.HTTP_200_OK)

    @decorators.action(
        detail=True,
        methods=["post"],
        url_path="submit",
        serializer_class=SubmitResultsTournamentSerializer,
    )
    def submit_result_to_tournament(self, request, id=None):
        tournament = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["player"]["name"]
        try:
            player_name = tournament.players.get(name=name)
        except PlayerName.DoesNotExist:
            raise exceptions.ValidationError(
                detail=f"Player {name} is not in tournament"
            )

        tournament.data = Judge(config=tournament.judge_config).update_result(
            tournament.data,
            player_name=player_name.name,
            round_id=serializer.validated_data["round_id"],
            score=serializer.validated_data["score"],
        )
        tournament.save()
        return Response(TournamentSerializer(tournament).data)
