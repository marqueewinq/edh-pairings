import typing as ty

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from rest_framework import exceptions, serializers, validators


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        id_field = attrs.get("username")
        password = attrs.get("password")

        user: ty.Optional[User]
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {
                "required": True,
                "validators": [validators.UniqueValidator(queryset=User.objects.all())],
            },
        }


class SendLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
