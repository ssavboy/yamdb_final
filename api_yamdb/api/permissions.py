from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Этот класс используется для определения
    кастомных полномочий для разрешения редактирования, удаления
    объекта автором, модератором, администритором.
    """

    def has_permission(self, request, view):
        """Разрешение на доступ к типу запроса."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Разрешение на доступ к объекту."""
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)
