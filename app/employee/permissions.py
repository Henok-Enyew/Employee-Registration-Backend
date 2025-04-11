from rest_framework import permissions
from core.enums import RoleChoices
from rest_framework.exceptions import PermissionDenied

class IsVerified(permissions.BasePermission):
    """
    Allows access only to Verifed Users
    """
    message = "Please verify your email address to access this resource."
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_verified):
            raise PermissionDenied(detail=self.message)
        return True
    

class IsHRManager(permissions.BasePermission):
    """
    Allows access only to admin users (role='admin')
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == RoleChoices.HR_MANAGER)

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access to object owners or admins
    """
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.role == 'admin' or 
            obj.user == request.user
        )