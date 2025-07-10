from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    message = "Требуются права модератора."

    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='moderator').exists()

class IsOwner(BasePermission):
    message = "Только владелец может управлять этим объектом."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user