from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from user_manager.core.domain.exceptions import (
    DeactivatedUser,
    RoleAlreadyAssigned,
    RoleNotAssigned,
    UserMustHaveAtLeastOneRole,
)
from user_manager.core.domain.user_role import UserRole


class User:
    def __init__(
        self,
        id: UUID,
        full_name: str,
        user_name: str,
        email: str,
        date_of_birth: date,
        password_hash: str,
        is_active: bool,
        created_at: datetime,
        updated_at: datetime,
        roles: set[UserRole],
    ) -> None:
        self.id = id
        self.full_name = full_name
        self.user_name = user_name
        self.email = email
        self.date_of_birth = date_of_birth
        self.password_hash = password_hash
        self.is_active = is_active
        self._created_at = created_at
        self.updated_at = updated_at
        if not roles:
            raise UserMustHaveAtLeastOneRole('User must have at least one role')
        self._roles = set(roles)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def roles(self) -> frozenset[UserRole]:
        return frozenset(self._roles)

    def _touch(self) -> None:
        self.updated_at = datetime.now(tz=timezone.utc)

    def _ensure_active(self) -> None:
        if not self.is_active:
            raise DeactivatedUser('user is not active')

    def deactivate(self) -> None:
        self.is_active = False
        self._touch()

    def is_admin(self) -> bool:
        return UserRole.ADMIN in self._roles

    def grant_role(self, role: UserRole) -> None:
        if role in self._roles:
            raise RoleAlreadyAssigned('User already has this role')

        self._roles.add(role)
        self._touch()

    def revoke_role(self, role: UserRole) -> None:
        if role not in self._roles:
            raise RoleNotAssigned('User doesn`t have this role')
        if len(self._roles) == 1:
            raise UserMustHaveAtLeastOneRole('User must have at least one role')

        self._roles.remove(role)
        self._touch()

    def update_full_name(self, new_name: str) -> None:
        self._ensure_active()
        self.full_name = new_name
        self._touch()

    def update_email(self, new_email: str) -> None:
        self._ensure_active()
        self.email = new_email
        self._touch()

    def update_password_hash(self, new_password_hash: str) -> None:
        self._ensure_active()
        self.password_hash = new_password_hash
        self._touch()

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        attrs = self.__dict__.items()
        hidden = {'password_hash'}
        internal_data = ', '.join(
            f'{k}={v!r}' for k, v in attrs if k not in hidden
        )
        return f'<User {internal_data}>'

    @classmethod
    def create(
        cls,
        full_name: str,
        user_name: str,
        email: str,
        date_of_birth: date,
        password_hash: str,
        roles: set[UserRole] | None = None,
    ) -> User:
        now: datetime = datetime.now(tz=timezone.utc)
        return cls(
            id=uuid4(),
            full_name=full_name,
            user_name=user_name,
            email=email,
            date_of_birth=date_of_birth,
            password_hash=password_hash,
            is_active=True,
            created_at=now,
            updated_at=now,
            roles=roles or {UserRole.USER},
        )
