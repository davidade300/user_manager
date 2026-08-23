from typing import Protocol
from uuid import UUID

from user_manager.core.domain.user import User


class UserRepository(Protocol):
    """Secondary port for User persistence.

    Implemented by driven adapters (e.g. a SQLAlchemy repository). Methods
    take and return domain ``User`` entities — never ORM models; translating
    between the two is the adapter's responsibility (via its mapper).
    """

    def get_by_id(self, user_id: UUID) -> User:
        """get a user by its id.

        Args:
            user_id: The user id.

        Returns:
            The matching ``User``, or ``None`` if no user has that id.
        """
        ...

    def get_by_username(self, user_name: str) -> User | None:
        """get a user by username (the login key).

        Args:
            user_name: The unique username to look up.

        Returns:
            The matching ``User``, or ``None`` if none exists.
        """
        ...

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email.

        Used for unique checks, when creating a user or updating
        their email address.

        Args:
            email: The email address to look up.

        Returns:
            The matching ``User``, or ``None`` if none exists.
        """
        ...

    def save(self, user: User) -> None:
        """Persist a user, creating it or updating it if it already exists.

        Args:
            user: The domain ``User`` entity to persist.
        """
        ...

    def exists_by_email(self, email: str) -> bool: ...

    def exists_by_user_name(self, user_name: str) -> bool: ...
