from uuid import UUID

from user_manager.core.domain.exceptions import (
    InsufficientPrivileges,
    InvalidCredentials,
    UserNotFound,
)
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import ChangeUserPasswordUseCase
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.user_repository import UserRepository


class ChangeUserPassword(ChangeUserPasswordUseCase):
    """Concrete implementation of the ``ChangeUserPasswordUseCase`` port.

    Self-service: authorizes the actor (must be the target user), verifies the
    current password via the ``PasswordHasher`` port, then hashes and stores
    the new one, persisting via the ``UserRepository``.
    """

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ) -> None:
        """Initialize the use case with its collaborators.

        Args:
            user_repository: Port used to look the user up and persist it.
            password_hasher: Port used to verify the current password and hash
                the new one.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(
        self,
        actor: User,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change a user's own password after verifying the current one.

        The full contract (parameters and raised exceptions) is defined on the
        ``ChangeUserPasswordUseCase`` port. This implementation authorizes the
        actor (must be the target user), loads the user, verifies the current
        password, then applies the hashed new password via the entity and
        persists it.
        """
        if actor.id != user_id:
            raise InsufficientPrivileges(
                f'User {actor.user_name} lacks the privileges to execute this operation'
            )

        user: User | None = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFound(f'User with id {user_id} not found')

        if not self.password_hasher.verify(
            current_password, user.password_hash
        ):
            raise InvalidCredentials('Current password is incorrect')

        user.change_password_hash(self.password_hasher.hash(new_password))
        self.user_repository.save(user)
