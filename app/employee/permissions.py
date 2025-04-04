from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users (role='admin')
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'admin')

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access to object owners or admins
    """
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.role == 'admin' or 
            obj.user == request.user
        )