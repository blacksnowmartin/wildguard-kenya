from collections.abc import Iterable

from rest_framework.permissions import BasePermission

from .models import User


class HasRole(BasePermission):
    allowed_roles: Iterable[str] = ()

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsRangerOrSupervisor(HasRole):
    allowed_roles = (User.Role.RANGER, User.Role.SUPERVISOR, User.Role.ADMIN)


class IsSupervisorOrAdmin(HasRole):
    allowed_roles = (User.Role.SUPERVISOR, User.Role.ADMIN)
