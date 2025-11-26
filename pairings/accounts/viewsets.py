from accounts.auth import validate_token
from accounts.mailing import send_mail_login_link
from accounts.permissions import IsAccountOwnerOrCreateOnly
from accounts.serializers import SendLinkSerializer, UserSerializer
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from rest_framework import decorators, mixins, response, status, throttling, viewsets
from django.contrib import messages


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAccountOwnerOrCreateOnly]
    throttle_classes = [throttling.AnonRateThrottle]

    def get_queryset(self):
        if self.request.user is None:
            return User.objects.none()
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj

    @decorators.action(
        detail=False,
        methods=["post"],
        url_path=r"send-link",
        serializer_class=SendLinkSerializer,
    )
    def send_link(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        user = User.objects.filter(email=email).first()
        if user is None:
            user = User.objects.create(email=email, username=email.split("@")[0])
        send_mail_login_link(user)
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=["get"],
        url_path=r"loginless/(?P<token>.+)",
    )
    def loginless(self, request, token):
        user = validate_token(token)
        if user is not None:
            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
        else:
            messages.error(request, "Login link is invalid or has expired. Please request a new one.")
        return redirect("index")
