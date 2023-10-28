from rest_framework import permissions

from .models import BaseModel


class IsOwnAccount(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: BaseModel):
        return obj.account == request.user
