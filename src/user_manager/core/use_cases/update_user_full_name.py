from uuid import UUID

from user_manager.core.domain.exceptions import (
    InsufficientPrivileges,
    UserNotFound,
)
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import UpdateUserFullNameUseCase
from user_manager.core.ports.secondary.user_repository import UserRepository


class UpdateUserFullName(UpdateUserFullNameUseCase):
    """Concrete implementation of the ``UpdateUserFullNameUseCase`` port.

    Authorizes the actor (admin or the target user), looks the user up by id
    via the ``UserRepository``, updates their full name through the entity, and
    persists the change.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the use case with its collaborator.

        Args:
            user_repository: Port used to look the user up and persist it.
        """
        self.user_repository = user_repository

    def execute(self, actor: User, user_id: UUID, new_full_name: str) -> None:
        """Update a user's full name, if the actor is authorized.

        The full contract (parameters and raised exceptions) is defined on the
        ``UpdateUserFullNameUseCase`` port. This implementation authorizes the
        actor, loads the user (raising ``UserNotFound`` if none exists), applies
        the change via the entity, and persists it.
        """
        if actor.id != user_id and not actor.is_admin():
            raise InsufficientPrivileges(
                f'User {actor.user_name} lacks the privileges to execute this operation'
            )
        user: User | None = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFound(f'User with id {user_id} not found')
        user.update_full_name(new_full_name)
        self.user_repository.save(user)
