from rest_framework.permissions import BasePermission

class IsVerifiedUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.verified)