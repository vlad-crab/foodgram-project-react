from rest_framework.permissions import BasePermission


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method is "GET" or obj.author == request.user
                or request.user.is_admin)


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
