from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.owner == request.user

class CustomIsAdminUser(permissions.BasePermission):
    
    def has_permission(self, request, view):
        METHOD = ['POST']
        if request.method not in METHOD:
            return True
        return request.user.is_staff
    
    
    