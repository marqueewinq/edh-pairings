from django.shortcuts import redirect, render
from django.urls import reverse
from news.models import NewsEntry
from pods.models import Tournament
from rest_framework.authtoken.models import Token


def index(request):
    token = ""
    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user).first()
    tours = Tournament.objects.all().order_by("-date_created")
    return render(
        request,
        "frontend/index.html",
        {
            "tournaments": tours,
            "token": token,
            "latest_news": NewsEntry.objects.order_by("-date_created").first(),
        },
    )


def detail(request, id):
    token = ""
    if request.user.is_authenticated:
        token = Token.objects.filter(user=request.user).first()
    tournament = Tournament.objects.filter(id=id).first()
    if tournament is None:
        return redirect(reverse("index"))
    return render(
        request,
        "frontend/detail.html",
        {
            "tournament": tournament,
            "token": token,
            "latest_news": NewsEntry.objects.order_by("-date_created").first(),
        },
    )
