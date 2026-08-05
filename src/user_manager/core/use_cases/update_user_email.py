from uuid import UUID

from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    InsufficientPrivileges,
    UserNotFound,
)
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import UpdateUserEmailUseCase
from user_manager.core.ports.secondary.user_repository import UserRepository


class UpdateUserEmail(UpdateUserEmailUseCase):
    """Concrete implementation of the ``UpdateUserEmailUseCase`` port.

    Authorizes the actor (admin or the target user), enforces email uniqueness
    via the ``UserRepository``, looks the user up by id, updates their email
    through the entity, and persists the change.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the use case with its collaborator.

        Args:
            user_repository: Port used to check email uniqueness, look the user
                up, and persist it.
        """
        self.user_repository = user_repository

    def execute(self, actor: User, user_id: UUID, new_email: str) -> None:
        """Update a user's email address, if the actor is authorized.

        The full contract (parameters and raised exceptions) is defined on the
        ``UpdateUserEmailUseCase`` port. This implementation authorizes the
        actor, rejects an email already in use, loads the user (raising
        ``UserNotFound`` if none exists), applies the change via the entity, and
        persists it.
        """
        if actor.id != user_id and not actor.is_admin():
            raise InsufficientPrivileges(
                f'User {actor.user_name} lacks the privileges to execute this operation'
            )
        if self.user_repository.get_by_email(new_email) is not None:
            raise EmailAlreadyInUse(f'A user with this email already exists.')
        user: User | None = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFound(f'User with id {user_id} not found')
        user.update_email(new_email)
        self.user_repository.save(user)
