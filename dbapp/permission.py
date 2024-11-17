from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from .models import User

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        email = getattr(request, 'auth_email', None)
        password = getattr(request, 'auth_password', None)
        print(email)
        print(password)

        if not email or not password:
            raise AuthenticationFailed("Authorization credentials are missing or invalid.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password.")

        if password != user.password:
            raise AuthenticationFailed("Invalid email or password.")

        if user.role != 'Admin':
            raise PermissionDenied("You do not have permission to perform this action.")

        request.user = user

        return True
