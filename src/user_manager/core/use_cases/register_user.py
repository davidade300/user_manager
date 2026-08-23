from datetime import date

from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    UsernameAlreadyInUse,
)
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import RegisterUserUseCase
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.user_repository import UserRepository


class RegisterUser(RegisterUserUseCase):
    """Concrete implementation of the ``RegisterUserUseCase`` port.

    Public self-registration: enforces email and username uniqueness via the
    ``UserRepository``, hashes the password via the ``PasswordHasher`` port,
    creates the user with the default ``USER`` role, persists it, and returns
    it.
    """

    def __init__(
        self, repository: UserRepository, password_hasher: PasswordHasher
    ) -> None:
        """Initialize the use case with its collaborators.

        Args:
            repository: Port used to check uniqueness and persist the user.
            password_hasher: Port used to hash the plain-text password.
        """
        self.repository = repository
        self.password_hasher = password_hasher

    def execute(
        self,
        full_name: str,
        user_name: str,
        email: str,
        date_of_birth: date,
        password: str,
    ) -> User:
        """Register a new user with the default ``USER`` role.

        The full contract (parameters, return value, and raised exceptions) is
        defined on the ``RegisterUserUseCase`` port. This implementation checks
        email then username uniqueness, hashes the password, builds the user
        via ``User.create``, persists it, and returns it.
        """

        if self.repository.exists_by_user_name(user_name):
            raise UsernameAlreadyInUse(
                f'A user with username {user_name} already exists.'
            )

        if self.repository.exists_by_email(email):
            raise EmailAlreadyInUse(
                f'A user with email {email} already exists.'
            )

        hashed_password: str = self.password_hasher.hash(password)
        user: User = User.create(
            full_name, user_name, email, date_of_birth, hashed_password
        )
        self.repository.save(user)
        return user
