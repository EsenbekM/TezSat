from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS


class IsBusiness(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return bool(is_authenticated and hasattr(request.user, 'business') and request.user.business.is_active)


class IsBusinessOrAdmin(IsBusiness):
    def has_permission(self, request, view):
        is_authenticated = super(IsBusinessOrAdmin, self).has_permission(request, view)
        return is_authenticated or request.user.is_staff


class IsBusinessManyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business == request.user.business


class IsBusinessOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated and request.user.business.is_active

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated and request.user.business.is_active
