from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or
                    request.user and request.user.is_staff)


class ViewCustomerHistory(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')
