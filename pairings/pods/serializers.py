from rest_framework import serializers
from pods.models import Tournament, PlayerName
from pods.judge import get_standings, get_rounds, update_result
from django.contrib.auth.models import User


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
        return get_standings(obj.data)

    def get_rounds(self, obj):
        return get_rounds(obj.data)

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
        )
        depth = 1


class AddPlayerToTournamentSerializer(serializers.Serializer):
    player = PlayerNameSerializer(required=True)

    def create(self, validated_data):
        name = validated_data["player"]["name"]
        player = PlayerName.objects.filter(name=name).first()
        if player is None:
            player = PlayerName.objects.create(name=name)
        return player


class SubmitResultsTournamentSerializer(serializers.Serializer):
    tournament = serializers.PrimaryKeyRelatedField(queryset=Tournament.objects)
    player = PlayerNameSerializer(required=True)
    round_id = serializers.IntegerField(required=True)
    score = serializers.JSONField(required=True)

    def create(self, validated_data):
        tour = validated_data["tournament"]
        tour.data = update_result(
            tour.data,
            player_name=validated_data["player"]["name"],
            round_id=validated_data["round_id"],
            score=validated_data["score"],
        )
        tour.save()
        return tour

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        id_field = attrs.get('username')

        user = None

        if '@' in id_field:
            user = User.objects.filter(email__iexact=id_field).first()
        elif id_field.isdigit():
            user = User.objects.filter(phone_number=id_field).first()
        else:
            user = User.objects.filter(username__iexact=id_field).first()

        if not user:
            raise serializers.ValidationError(f"User {attrs} does not exist")

        attrs["user"] = user

        return attrs