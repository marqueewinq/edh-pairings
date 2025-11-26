from pods.models import Tournament
from rest_framework import permissions


class IsTournamentOwnerOrReadOnly(permissions.BasePermission):
    message = "Users are not allowed to change objects they do not own."

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Tournament):
            return True
        return (
            request.method in permissions.SAFE_METHODS  # read-only request is okay
            or request.user.is_staff  # admins can do anything
            or obj.owner is None  # legacy tournaments are open to anybody
            or obj.owner == request.user  # owners can manage their tournaments
        )
