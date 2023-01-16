from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from judge import Judge
from pods.models import PlayerName, Tournament
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
        return Judge().get_standings(obj.data)

    def get_rounds(self, obj):
        return Judge().get_rounds(obj.data)

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
    player = PlayerNameSerializer(required=True)
    round_id = serializers.IntegerField(required=True)
    score = serializers.JSONField(required=True)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        id_field = attrs.get("username")
        password = attrs.get("password")

        user = None

        if "@" in id_field:
            user = User.objects.filter(email__iexact=id_field).first()
        else:
            user = User.objects.filter(username__iexact=id_field).first()

        if not user or not check_password(password, user.password):
            raise exceptions.AuthenticationFailed(
                detail=f"User {id_field} does not exist or credentials are incorrect."
            )

        attrs["user"] = user

        return attrs
