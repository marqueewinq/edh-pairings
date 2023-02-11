from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from news.models import NewsEntry
from pods.models import Tournament
from rest_framework.authtoken.models import Token


def get_user_auth_token(request) -> str:
    if request.user.is_authenticated:
        token, _ = Token.objects.get_or_create(user=request.user)
        return token
    return ""


def index(request):
    tours = Tournament.objects.all().order_by("-date_created")
    return render(
        request,
        "frontend/index.html",
        {
            "tournaments": tours,
            "token": get_user_auth_token(request),
            "latest_news": NewsEntry.objects.order_by("-date_created").first(),
            "donate_link_ru": settings.DONATE_LINK_RU,
        },
    )


def detail(request, id):
    tournament = Tournament.objects.filter(id=id).first()
    if tournament is None:
        return redirect(reverse("index"))
    return render(
        request,
        "frontend/detail.html",
        {
            "tournament": tournament,
            "token": get_user_auth_token(request),
            "latest_news": NewsEntry.objects.order_by("-date_created").first(),
            "donate_link_ru": settings.DONATE_LINK_RU,
            "to_show_control_buttons": request.user.is_authenticated
            and (tournament.owner is None or tournament.owner == request.user),
        },
    )
