from rest_framework.permissions import BasePermission

class IsAuthenticatedWithMFA(BasePermission):
    message = "User must complete MFA verification."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, "mfa_enabled", False)
