"""Domain exceptions for the ``user_manager`` core.

Every exception inherits from ``DomainException`` so callers (use cases,
adapters) can catch the whole family or a specific failure. They are raised by
the domain entity and the use cases; delivery adapters translate them into
transport-level errors (e.g. HTTP status codes) at the edge.
"""


class DomainException(Exception):
    """Base class for all domain-level errors raised by the core."""


class UserMustHaveAtLeastOneRole(DomainException):
    """Raised when an operation would leave a user with no roles."""


class RoleNotAssigned(DomainException):
    """Raised when revoking a role the user does not have."""


class RoleAlreadyAssigned(DomainException):
    """Raised when granting a role the user already has."""


class DeactivatedUser(DomainException):
    """Raised when an operation requires an active user but the user is not."""


class InsufficientPrivileges(DomainException):
    """Raised when the actor lacks the privileges for the requested operation."""


class EmailAlreadyInUse(DomainException):
    """Raised when an email is already registered to another user."""


class UsernameAlreadyInUse(DomainException):
    """Raised when a username is already taken by another user."""


class InvalidCredentials(DomainException):
    """Raised when authentication fails.

    Uniform for both an unknown username and a wrong password, so callers
    cannot tell which failed (avoids user enumeration).
    """


class InvalidUsername(DomainException):
    """Raised when a username is empty or blank."""


class InvalidEmail(DomainException):
    """Raised when an email is empty or blank."""


class UserNotFound(DomainException):
    """Raised when no user matches the given identifier."""
