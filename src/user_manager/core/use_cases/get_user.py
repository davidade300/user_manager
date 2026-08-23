from uuid import UUID

from user_manager.core.domain.exceptions import InsufficientPrivileges
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import GetUserUseCase
from user_manager.core.ports.secondary.user_repository import UserRepository


class GetUser(GetUserUseCase):
    """Concrete implementation of the ``GetUserUseCase`` port.

    Authorizes the actor (must be an admin or the target user), then looks the
    user up by id via the ``UserRepository``.
    """

    def __init__(self, repository: UserRepository) -> None:
        """Initialize the use case with its collaborator.

        Args:
            repository: Port used to look the user up by id.
        """
        self.repository = repository

    def execute(self, actor: User, user_id: UUID) -> User:
        """Retrieve a user by id after authorizing the actor.

        The full contract (parameters, return value, and raised exceptions) is
        defined on the ``GetUserUseCase`` port. This implementation authorizes
        the actor (must be an admin or the target user), then returns the
        repository lookup by id or raises ``UserNotFound``.
        """
        if actor.id != user_id and not actor.is_admin():
            raise InsufficientPrivileges(
                f'User {actor.user_name} lacks the privileges to execute this operation'
            )

        return self.repository.get_by_id(user_id)
