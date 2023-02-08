import marshmallow as ma
from judge import Judge
from pods.models import PlayerName, Tournament
from pods.schemas import TournamentSettingsSchema
from rest_framework import exceptions, serializers


class PlayerNameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = PlayerName
        fields = ("id", "name")


class TournamentSerializer(serializers.ModelSerializer):
    players = PlayerNameSerializer(many=True, required=False)
    standings = serializers.SerializerMethodField()
    rounds = serializers.SerializerMethodField()

    def get_standings(self, obj):
        return Judge(config=obj.judge_config).get_standings(obj.data)

    def get_rounds(self, obj):
        return Judge(config=obj.judge_config).get_rounds(obj.data)

    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "date_created",
            "date_updated",
            "status",
            "players",
            "standings",
            "rounds",
            "settings",
        )
        depth = 1

    def validate(self, data):
        if "settings" in data:
            try:
                data["settings"] = TournamentSettingsSchema().load(data["settings"])
            except ma.exceptions.ValidationError as e:
                raise exceptions.ValidationError(e)
        return data


class BulkEditPlayersSerializer(serializers.Serializer):
    players = PlayerNameSerializer(many=True, required=True)


class AddPlayerToTournamentSerializer(serializers.Serializer):
    player = PlayerNameSerializer(required=True)

    def create(self, validated_data):
        name = validated_data["player"]["name"]
        player = PlayerName.objects.filter(name=name).first()
        if player is None:
            player = PlayerName.objects.create(name=name)
        return player


class SubmitResultsTournamentSerializer(serializers.Serializer):
    player = PlayerNameSerializer(required=True)
    round_id = serializers.IntegerField(required=True)
    score = serializers.JSONField(required=True)
