from rest_framework import permissions


class OwnerOrReadPermission(permissions.BasePermission):
    """Разрешения для безопасных методов, либо собственникам контента,
       либо для администратора
    """

    message = 'Для редактирования Вы должны быть автором контента.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or request.user.is_superuser
            or obj.author == request.user)
