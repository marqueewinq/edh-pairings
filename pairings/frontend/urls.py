from django.urls import path
from frontend import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tournaments/<int:id>/", views.detail, name="detail"),
]
