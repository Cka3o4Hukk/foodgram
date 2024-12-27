from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверка на аутентификацию и авторство"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
