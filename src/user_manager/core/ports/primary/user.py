from dataclasses import dataclass
from datetime import date
from typing import Protocol
from uuid import UUID

from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole


@dataclass(frozen=True)
class AuthResult:
    """Outcome of a successful authentication.

    Value object bundling the authenticated user with the access token issued
    for them, so a caller gets both the credential to carry on later requests
    and the user's data without a second round-trip.

    Attributes:
        user: The authenticated ``User`` entity.
        access_token: The signed access token issued for the user.
    """

    user: User
    access_token: str


class CreateUserUseCase(Protocol):
    """Primary port for creating a new user (admin only).

    The implementation authorizes the actor (must be an admin), hashes the
    given password via the ``PasswordHasher`` port, enforces uniqueness of the
    username and email via the ``UserRepository``, and persists the new user.
    """

    def execute(
        self,
        actor: User,
        full_name: str,
        user_name: str,
        email: str,
        date_of_birth: date,
        password: str,
        roles: set[UserRole] | None = None,
    ) -> User:
        """Create a new user with the given details.

        Args:
            actor: The authenticated user performing the action; must be an
                admin.
            full_name: The user's full name.
            user_name: The unique username used for login.
            email: The user's email address.
            date_of_birth: The user's date of birth.
            password: The plain-text password; hashed before storage.
            roles: Optional set of roles; defaults to ``{UserRole.USER}``.

        Returns:
            The created ``User`` domain entity.

        Raises:
            InsufficientPrivileges: If the actor is not an admin.
            InvalidUsername: If the username is empty or blank.
            InvalidEmail: If the email is empty or blank.
            UsernameAlreadyInUse: If the username is already taken.
            EmailAlreadyInUse: If the email is already used by another user.
        """
        ...


class GetUserUseCase(Protocol):
    """Primary port for retrieving a user by id (admin or the user themselves)."""

    def execute(self, actor: User, user_id: UUID) -> User | None:
        """Retrieve a user by their unique id.

        Args:
            actor: The authenticated user performing the action; must be an
                admin or the target user.
            user_id: The unique identifier of the user to retrieve.

        Returns:
            The matching ``User`` entity, or ``None`` if none exists.

        Raises:
            InsufficientPrivileges: If the actor is neither an admin nor the
                target user.
        """
        ...


class UpdateUserFullNameUseCase(Protocol):
    """Primary port for updating a user's full name (admin or the user)."""

    def execute(self, actor: User, user_id: UUID, new_full_name: str) -> None:
        """Update a user's full name.

        Args:
            actor: The authenticated user performing the action; must be an
                admin or the target user.
            user_id: The unique identifier of the user to update.
            new_full_name: The new full name to set.

        Raises:
            InsufficientPrivileges: If the actor is neither an admin nor the
                target user.
            UserNotFound: If no user has the given id.
            DeactivatedUser: If the user is not active.
        """
        ...


class UpdateUserEmailUseCase(Protocol):
    """Primary port for updating a user's email (admin or the user).

    The implementation enforces email uniqueness across users via the
    ``UserRepository``.
    """

    def execute(self, actor: User, user_id: UUID, new_email: str) -> None:
        """Update a user's email address.

        The new email must not already belong to another user.

        Args:
            actor: The authenticated user performing the action; must be an
                admin or the target user.
            user_id: The unique identifier of the user to update.
            new_email: The new email address to set.

        Raises:
            InsufficientPrivileges: If the actor is neither an admin nor the
                target user.
            EmailAlreadyInUse: If the email is already used by another user.
            UserNotFound: If no user has the given id.
            DeactivatedUser: If the user is not active.
        """
        ...


class ChangeUserPasswordUseCase(Protocol):
    """Primary port for a user changing their own password.

    The implementation verifies the current password via the
    ``PasswordHasher`` port before hashing and storing the new one.
    """

    def execute(
        self,
        actor: User,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change a user's password after verifying the current one.

        Args:
            actor: The authenticated user performing the action; must be the
                target user.
            user_id: The unique identifier of the user.
            current_password: The current plain-text password, verified
                before the change is applied.
            new_password: The new plain-text password; hashed before storage.

        Raises:
            InsufficientPrivileges: If the actor is not the target user.
            InvalidCredentials: If the current password does not match.
        """
        ...


class ResetUserPasswordUseCase(Protocol):
    """Primary port for resetting a user's password (admin only).

    Unlike changing a password, this does not require the current password:
    an admin sets a new one directly. The implementation hashes the new
    password via the ``PasswordHasher`` port and stores it.
    """

    def execute(self, actor: User, user_id: UUID, new_password: str) -> None:
        """Reset a user's password to a new value.

        Args:
            actor: The authenticated user performing the action; must be an
                admin.
            user_id: The unique identifier of the user whose password is reset.
            new_password: The new plain-text password; hashed before storage.

        Raises:
            InsufficientPrivileges: If the actor is not an admin.
        """
        ...


class RegisterUserUseCase(Protocol):
    """Primary port for public self-registration.

    Unauthenticated sign-up: there is no actor, and the caller cannot choose
    roles — the new user always gets ``{UserRole.USER}``. The implementation
    hashes the password via the ``PasswordHasher`` port, enforces uniqueness
    of the username and email via the ``UserRepository``, and persists the
    new user.
    """

    def execute(
        self,
        full_name: str,
        user_name: str,
        email: str,
        date_of_birth: date,
        password: str,
    ) -> User:
        """Register a new user with the default ``USER`` role.

        Args:
            full_name: The user's full name.
            user_name: The unique username used for login.
            email: The user's email address.
            date_of_birth: The user's date of birth.
            password: The plain-text password; hashed before storage.

        Returns:
            The created ``User`` domain entity.

        Raises:
            InvalidUsername: If the username is empty or blank.
            InvalidEmail: If the email is empty or blank.
            UsernameAlreadyInUse: If the username is already taken.
            EmailAlreadyInUse: If the email is already used by another user.
        """
        ...


class AuthenticateUserUseCase(Protocol):
    """Primary port for authenticating a user and issuing an access token.

    Public (unauthenticated): verifies the username/password pair (reusing the
    credential check) and, on success, issues an access token via the
    ``TokenIssuer`` port. Returns both the user and the token, so the caller can
    carry the token on later requests and read the user's data without a second
    round-trip. This is the JWT-style login; per-request schemes such as Basic
    Auth use ``VerifyCredentialsUseCase`` instead.
    """

    def execute(self, user_name: str, password: str) -> AuthResult:
        """Authenticate a user and return the user together with a token.

        Args:
            user_name: The username used for login.
            password: The plain-text password, checked against the stored hash.

        Returns:
            An ``AuthResult`` bundling the authenticated ``User`` and the issued
            access token.

        Raises:
            InvalidCredentials: If the username is unknown or the password does
                not match. The same exception is raised in both cases so callers
                cannot tell which failed (avoids user enumeration).
        """
        ...


class VerifyUserCredentialsUseCase(Protocol):
    """Primary port for verifying a user's credentials without issuing a token.

    Public (unauthenticated): looks the user up by username via the
    ``UserRepository`` and checks the plain-text password against the stored
    hash via the ``PasswordHasher`` port. Used for per-request schemes such as
    HTTP Basic Auth and for step-up re-authentication. Returns the ``User`` so
    the caller can read its roles for authorization.
    """

    def execute(self, user_name: str, password: str) -> User:
        """Verify a username/password pair and return the matching user.

        Args:
            user_name: The username used for login.
            password: The plain-text password, checked against the stored hash.

        Returns:
            The authenticated ``User`` domain entity.

        Raises:
            InvalidCredentials: If the username is unknown or the password does
                not match. The same exception is raised in both cases so callers
                cannot tell which failed (avoids user enumeration).
        """
        ...
