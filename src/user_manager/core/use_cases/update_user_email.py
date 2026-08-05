from uuid import UUID

from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    InsufficientPrivileges,
)
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import UpdateUserEmailUseCase


class UpdateUserEmail(UpdateUserEmailUseCase):
    def __init__(self, user_repository) -> None:
        self.user_repository = user_repository

    def execute(self, actor: User, user_id: UUID, new_email: str) -> None:
        """Update a user's full name."""
        if actor.id != user_id and not actor.is_admin():
            raise InsufficientPrivileges(
                f'User {actor.user_name} lacks the privileges to execute this operation'
            )
        if self.user_repository.get_by_email(new_email) is not None:
            raise EmailAlreadyInUse(f'A user with this email already exists.')
        user: User = self.user_repository.get_by_id(user_id)
        user.update_email(new_email)
        self.user_repository.save(user)
