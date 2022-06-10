from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

    def has_permission(self, request, view):
        return request.user.is_authenticated


class CustomIsAdminUser(permissions.BasePermission):
    
    def has_permission(self, request, view):

        return request.user.is_staff

