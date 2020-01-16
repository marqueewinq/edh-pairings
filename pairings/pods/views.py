from django.shortcuts import render
from pods.models import Tournament


def index(request):
    tours = Tournament.objects.all().order_by("date_created")
    return render(request, "pods/index.html", {"tournaments": tours})
