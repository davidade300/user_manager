from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from user_manager.core.domain.exceptions import (
    DeactivatedUser,
    InvalidEmail,
    InvalidUsername,
    RoleAlreadyAssigned,
    RoleNotAssigned,
    UserMustHaveAtLeastOneRole,
)
from user_manager.core.domain.user_role import UserRole


class User:
    """Main domain entity encapsulating all user-related business rules.

    Covers role management, activation/deactivation, and personal
    information updates. Instances should be created through the
    ``User.create`` factory method rather than the constructor directly
    (the constructor is the raw reconstitution path, e.g. for the mapper).
    """

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
        """Reconstitute a ``User`` from complete data (e.g. the DB mapper).

        Prefer the ``create`` factory for new users; this constructor takes
        every field as-is and only enforces the entity's invariants.

        Raises:
            InvalidUsername: If the username is empty or blank.
            InvalidEmail: If the email is empty or blank.
            UserMustHaveAtLeastOneRole: If ``roles`` is empty.
        """
        self.id: UUID = id
        self.full_name: str = full_name
        if not user_name or user_name.isspace():
            raise InvalidUsername('user_name must be provided')
        self.user_name: str = user_name
        if not email or email.isspace():
            raise InvalidEmail('email must be provided')
        self.email: str = email
        self.date_of_birth: date = date_of_birth
        self.password_hash: str = password_hash
        self.is_active: bool = is_active
        self._created_at: datetime = created_at
        self.updated_at: datetime = updated_at
        if not roles:
            raise UserMustHaveAtLeastOneRole('User must have at least one role')
        self._roles: set[UserRole] = set(roles)

    @property
    def created_at(self) -> datetime:
        """The user's creation timestamp.

        Returns:
            The datetime the user was created.
        """
        return self._created_at

    @property
    def roles(self) -> frozenset[UserRole]:
        """The user's roles as an immutable set.

        Returns:
            A frozenset with the user's roles.
        """
        return frozenset(self._roles)

    def _touch(self) -> None:
        """Update ``updated_at`` to the current time.

        For internal use only; should be called after any state change.
        """
        self.updated_at = datetime.now(tz=timezone.utc)

    def _ensure_active(self) -> None:
        """Guard that the user is active. For internal use only.

        Raises:
            DeactivatedUser: If the user is not active.
        """
        if not self.is_active:
            raise DeactivatedUser('user is not active')

    def deactivate(self) -> None:
        """Deactivate the user and update the ``updated_at`` timestamp."""
        self.is_active = False
        self._touch()

    def is_admin(self) -> bool:
        """Return whether the user has the admin role.

        Returns:
            True if the user has the admin role, otherwise False.
        """
        return UserRole.ADMIN in self._roles

    def grant_role(self, role: UserRole) -> None:
        """Grant a role to the user and mark the object as updated.

        Args:
            role: The role to grant.

        Raises:

            RoleAlreadyAssigned: If the user already has the role.
            DeactivatedUser: If the user is not active.
        """

        self._ensure_active()

        if role in self._roles:
            raise RoleAlreadyAssigned('User already has this role')

        self._roles.add(role)
        self._touch()

    def revoke_role(self, role: UserRole) -> None:
        """Revoke a role from the user and mark the object as updated.

        Args:
            role: The role to revoke.

        Raises:
            RoleNotAssigned: If the user doesn't have the role.
            UserMustHaveAtLeastOneRole: If the role is the user's only one.
        """
        if role not in self._roles:
            raise RoleNotAssigned('User doesn`t have this role')
        if len(self._roles) == 1:
            raise UserMustHaveAtLeastOneRole('User must have at least one role')

        self._roles.remove(role)
        self._touch()

    def update_full_name(self, new_name: str) -> None:
        """Update the user's full name and mark the object as updated.

        Args:
            new_name: The new full name to set for the user.

        Raises:
            DeactivatedUser: If the user is not active.
        """
        self._ensure_active()
        self.full_name = new_name
        self._touch()

    def update_email(self, new_email: str) -> None:
        """Update the user's email address and mark the object as updated.

        Args:
            new_email: The new email address to set for the user.

        Raises:
            DeactivatedUser: If the user is not active.
        """
        self._ensure_active()
        self.email = new_email
        self._touch()

    def change_password_hash(self, new_password_hash: str) -> None:
        """Change the user's password hash and mark the object as updated.

        Unlike the profile updates, this is NOT guarded by ``is_active``: a
        password must be changeable even on a deactivated account (e.g. an
        admin resetting a compromised password before reactivating it).

        Args:
            new_password_hash: The new hashed password to set for the user.
        """
        self.password_hash = new_password_hash
        self._touch()

    def __eq__(self, other) -> bool:
        """Compare users by identity (``id``).

        Args:
            other: The object to compare with the current instance.

        Returns:
            True if ``other`` is a ``User`` with the same ``id``;
            ``NotImplemented`` if ``other`` is not a ``User``.
        """
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Return the hash of the user, based on its ``id``."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Return a string representation of the user, excluding ``password_hash``."""
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
        """Create a new user, generating the auto-managed fields.

        Factory method that generates ``id``, ``is_active``, ``created_at``
        and ``updated_at``. When no roles are given, defaults to
        ``{UserRole.USER}``.

        Args:
            full_name: The full name of the user.
            user_name: The unique username of the user.
            email: The email address of the user.
            date_of_birth: The date of birth of the user.
            password_hash: The hashed password of the user.
            roles: Optional set of roles. Defaults to ``{UserRole.USER}``.

        Returns:
            A new active ``User`` instance.
        """
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
