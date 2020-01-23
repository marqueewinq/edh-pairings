from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.authtoken.models import Token
from pods.models import Tournament

def index(request):
    token = ""
    if request.user.is_authenticated:
        token = Token.objects.filter(user = request.user).first()
    tours = Tournament.objects.all().order_by("-date_created")
    return render(request, "pods/index.html", {"tournaments": tours, "token": token})


def detail(request, id):
    token = ""
    if request.user.is_authenticated:
        token = Token.objects.filter(user = request.user).first()
    tournament = Tournament.objects.filter(id=id).first()
    if tournament is None:
        return redirect(reverse("index"))
    return render(request, "pods/detail.html", {"tournament": tournament, "token": token})
