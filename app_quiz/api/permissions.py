from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Allows access only to the creator (owner) of the object.
    """

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user
