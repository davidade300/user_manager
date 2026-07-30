from datetime import date

from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    InsufficientPrivileges,
    UsernameAlreadyInUse,
)
from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole
from user_manager.core.ports.primary.user import CreateUserUseCase
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.user_repository import UserRepository


class CreateUser(CreateUserUseCase):
    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self.repository = repository
        self.password_hasher = password_hasher

    def execute(
        self,
        actor: User,
        full_name: str,
        user_name: str,
        email: str,
        date_of_birth: date,
        password: str,
        roles: set[UserRole] | None = None,
    ) -> User:
        if not actor.is_admin():
            raise InsufficientPrivileges(
                f'User {actor.user_name} lacks the privileges to execute this action.'
            )
        if self.repository.get_by_email(email) is not None:
            raise EmailAlreadyInUse(
                f'A user with email {email} already exists.'
            )

        if self.repository.get_by_username(user_name) is not None:
            raise UsernameAlreadyInUse(
                f'A user with username {user_name} already exists.'
            )

        hashed_password: str = self.password_hasher.hash(password)
        user: User = User.create(
            full_name, user_name, email, date_of_birth, hashed_password
        )
        self.repository.save(user)
        return user
