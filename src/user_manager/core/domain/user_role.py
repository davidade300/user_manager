from enum import StrEnum


class UserRole(StrEnum):
    """
    Enumeration of user roles.

    Represents different roles assigned to users within the system.
    These roles can be used to define permissions, access levels,
    or functional responsibilities for users in the application.

    Attributes:
        ADMIN (str): Represents an administrative user with elevated privileges.
        USER (str): Represents a standard user with base-level permissions.
    """

    ADMIN = 'ADMIN'
    USER = 'USER'
