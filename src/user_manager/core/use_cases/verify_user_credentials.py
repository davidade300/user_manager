from user_manager.core.domain.exceptions import (
    InvalidCredentials,
)
from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import VerifyUserCredentialsUseCase
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.user_repository import UserRepository


class VerifyUserCredentials(VerifyUserCredentialsUseCase):
    """Concrete implementation of the ``VerifyUserCredentialsUseCase`` port.

    Public (unauthenticated): looks the user up by username via the
    ``UserRepository`` and checks the password against the stored hash via the
    ``PasswordHasher`` port. On an unknown username it still runs a dummy hash
    and verify so the response time does not reveal whether the user exists.
    """

    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ) -> None:
        """Initialize the use case with its collaborators.

        Args:
            user_repository: Port used to look the user up by username.
            password_hasher: Port used to verify the password against the hash.
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, user_name: str, password: str) -> User:
        """Verify a username/password pair and return the matching user.

        The full contract (parameters and raised exceptions) is defined on the
        ``VerifyUserCredentialsUseCase`` port. This implementation loads the
        user by username, verifies the password, and raises the same
        ``InvalidCredentials`` for both an unknown username and a wrong
        password, running a dummy hash/verify in the unknown-username branch to
        keep timing uniform (avoids user enumeration).
        """
        user: User | None = self.user_repository.get_by_username(user_name)

        if user is None:
            dummy_pwd: str = self.password_hasher.hash('dummy_123')
            self.password_hasher.verify('dummy_123', dummy_pwd)
            raise InvalidCredentials('Invalid user name or password')

        if not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentials('Invalid user name or password')

        return user
