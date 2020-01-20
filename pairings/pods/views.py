from django.shortcuts import render, redirect
from django.urls import reverse
from pods.models import Tournament


def index(request):
    tours = Tournament.objects.all().order_by("-date_created")
    return render(request, "pods/index.html", {"tournaments": tours})


def detail(request, id):
    tournament = Tournament.objects.filter(id=id).first()
    if tournament is None:
        return redirect(reverse("index"))
    return render(request, "pods/detail.html", {"tournament": tournament})
