from django.contrib.auth.models import AnonymousUser, User
from rest_framework import permissions


class IsAccountOwnerOrCreateOnly(permissions.BasePermission):
    message = "Users are not allowed to change objects they do not own."

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, AnonymousUser):
            return False
        if not isinstance(obj, User):
            return True
        return request.user.is_authenticated and request.user == obj
