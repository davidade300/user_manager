from uuid import UUID

from user_manager.core.domain.exceptions import (
    InsufficientPrivileges,
    UserNotFound,
)
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import ResetUserPasswordUseCase
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.user_repository import UserRepository


class ResetUserPassword(ResetUserPasswordUseCase):
    """Concrete implementation of the ``ResetUserPasswordUseCase`` port.

    Admin-only: authorizes the actor (must be an admin), looks the user up by
    id via the ``UserRepository``, then hashes and stores the new password.
    Unlike ``ChangeUserPassword``, it does not require the current password.
    """

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ) -> None:
        """Initialize the use case with its collaborators.

        Args:
            user_repository: Port used to look the user up and persist it.
            password_hasher: Port used to hash the new password.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, actor: User, user_id: UUID, new_password: str) -> None:
        """Reset a user's password to a new value, if the actor is an admin.

        The full contract (parameters and raised exceptions) is defined on the
        ``ResetUserPasswordUseCase`` port. This implementation authorizes the
        actor (must be an admin), loads the user (raising ``UserNotFound`` if
        none exists), then applies the hashed new password via the entity and
        persists it.
        """
        if not actor.is_admin():
            raise InsufficientPrivileges(
                'Only admins can reset user passwords.'
            )

        user: User | None = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFound(f'User with id {user_id} not found')

        user.change_password_hash(self.password_hasher.hash(new_password))
        self.user_repository.save(user)
