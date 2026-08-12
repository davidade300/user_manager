import pytest

from user_manager.core.domain.exceptions import InvalidCredentials
from user_manager.core.use_cases.authenticate_user import AuthenticateUser
from user_manager.core.use_cases.verify_user_credentials import (
    VerifyUserCredentials,
)
from ..fakes import FakePasswordHasher, FakeTokenIssuer, FakeUserRepository


@pytest.fixture
def authenticate_user(regular_user) -> AuthenticateUser:
    repo = FakeUserRepository()
    repo.save(regular_user)
    return AuthenticateUser(
        issuer=FakeTokenIssuer(),
        verifier=VerifyUserCredentials(repo, FakePasswordHasher()),
    )


class TestAuthenticateUserUseCase:
    def test_authenticate_returns_user_and_issued_token(
            self, regular_user, authenticate_user
    ) -> None:
        result = authenticate_user.execute(
            regular_user.user_name, 'senha_da_silva'
        )

        assert result.user == regular_user
        assert result.access_token == FakeTokenIssuer().issue(regular_user)

    def test_authenticate_user_with_wrong_password_raises(self, regular_user, authenticate_user) -> None:
        with pytest.raises(InvalidCredentials):
            authenticate_user.execute(regular_user.user_name, 'senha_errada')
