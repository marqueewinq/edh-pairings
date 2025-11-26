from accounts import viewsets
from rest_framework import routers

api_v1_router = routers.SimpleRouter()
api_v1_router.register(r"api/v1/accounts", viewsets.UserViewSet)

urlpatterns = api_v1_router.urls
