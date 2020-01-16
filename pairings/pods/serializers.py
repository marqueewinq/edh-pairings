from rest_framework import serializers
from pods.models import Tournament, PlayerName


class PlayerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only = True)
    class Meta:
        model = PlayerName
        fields = ("id", "name")

            
class TournamentSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    class Meta:
        model = Tournament
        fields = ("id", "name", "date_created", "date_updated", "status", "players")
        depth = 1

class AddPlayerToTournamentSerializer(serializers.Serializer):
    player = PlayerSerializer(required = True)

    def create(self, validated_data):
        name = validated_data["player"]["name"]
        player = PlayerName.objects.filter(name = name).first()
        if player is None:
            player = PlayerName.objects.create(name = name)
        return player

