from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import (
    AuthenticateUserUseCase,
    AuthResult,
)
from user_manager.core.ports.primary.user import VerifyUserCredentialsUseCase
from user_manager.core.ports.secondary.token_issuer import TokenIssuer


class AuthenticateUser(AuthenticateUserUseCase):
    """Concrete implementation of the ``AuthenticateUserUseCase`` port.

    JWT-style login: delegates credential checking to a
    ``VerifyUserCredentialsUseCase`` and, on success, issues an access token
    via the ``TokenIssuer`` port. Returns both the user and the token bundled
    in an ``AuthResult``. It owns no repository or hasher of its own — those
    live inside the injected verifier.
    """

    def __init__(self, issuer: TokenIssuer,
                 verifier: VerifyUserCredentialsUseCase) -> None:
        """Initialize the use case with its collaborators.

        Args:
            issuer: Port used to issue the access token for the user.
            verifier: Use case that verifies the username/password pair and
                returns the matching user.
        """
        self.issuer = issuer
        self.verifier = verifier

    def execute(self, user_name: str, password: str) -> AuthResult:
        """Authenticate a user and return the user together with a token.

        The full contract (parameters and raised exceptions) is defined on the
        ``AuthenticateUserUseCase`` port. This implementation verifies the
        credentials via the verifier (which raises ``InvalidCredentials`` on
        failure), issues an access token, and bundles both into an
        ``AuthResult``.
        """
        valid_user: User = self.verifier.execute(user_name, password)

        return AuthResult(valid_user, self.issuer.issue(valid_user))
