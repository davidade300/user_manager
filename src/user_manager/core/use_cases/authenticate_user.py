from user_manager.core.domain.user import User
from user_manager.core.ports.primary.user import (
    AuthenticateUserUseCase,
    AuthResult,
)
from user_manager.core.ports.primary.user import VerifyUserCredentialsUseCase
from user_manager.core.ports.secondary.token_issuer import TokenIssuer


class AuthenticateUser(AuthenticateUserUseCase):
    def __init__(self, issuer: TokenIssuer,
                 verifier: VerifyUserCredentialsUseCase) -> None:
        self.issuer = issuer
        self.verifier = verifier

    def execute(self, user_name: str, password: str) -> AuthResult:
        valid_user: User = self.verifier.execute(user_name, password)

        return AuthResult(valid_user, self.issuer.issue(valid_user))
