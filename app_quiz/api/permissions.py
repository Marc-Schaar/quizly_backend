from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Permission that allows access only to the creator (owner).

    This permission is intended for object-level checks. Use it to ensure
    that only the user who created a resource may modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        """Return True if `request.user` is the creator/owner of `obj`.

        Parameters:
        - request: Django REST Framework `Request` instance.
        - view: DRF view instance.
        - obj: The object being accessed (must have a `creator` attribute).
        """
        return obj.creator == request.user
