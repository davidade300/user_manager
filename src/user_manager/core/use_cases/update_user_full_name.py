from uuid import UUID

from user_manager.core.domain.exceptions import InsufficientPrivileges
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import UpdateUserFullNameUseCase


class UpdateUserFullName(UpdateUserFullNameUseCase):
    def __init__(self, user_repository) -> None:
        self.user_repository = user_repository

    def execute(self, actor: User, user_id: UUID, new_full_name: str) -> None:
        """Update a user's full name."""
        if actor.id != user_id and not actor.is_admin():
            raise InsufficientPrivileges(
                f'User {actor.user_name} lacks the privileges to execute this operation'
            )
        user: User = self.user_repository.get_by_id(user_id)
        user.update_full_name(new_full_name)
        self.user_repository.save(user)
