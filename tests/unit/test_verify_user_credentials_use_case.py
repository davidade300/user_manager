import pytest

from user_manager.core.domain.exceptions import (
    InvalidCredentials,
    InvalidUsername,
)
from user_manager.core.use_cases.verify_user_credentials import (
    VerifyUserCredentials,
)


@pytest.fixture
def user_in_repo(user_repository, regular_user):
    user_repository.save(regular_user)
    return regular_user


class TestVerifyUserCredentials:
    def test_verify_correct_credentials_works(
        self, user_in_repo, user_repository, password_hasher
    ) -> None:

        verify_user_credentials: VerifyUserCredentials = VerifyUserCredentials(
            user_repository, password_hasher
        )

        assert (
            verify_user_credentials.execute(
                user_name=user_in_repo.user_name, password='senha_da_silva'
            )
            == user_in_repo
        )

    def test_verify_with_incorret_username_raises(
        self, user_in_repo, user_repository, password_hasher
    ) -> None:
        verify_user_credentials: VerifyUserCredentials = VerifyUserCredentials(
            user_repository, password_hasher
        )

        with pytest.raises(InvalidCredentials):
            verify_user_credentials.execute(
                user_name='user_inexistente', password='senha_da_silva'
            )

    def test_verify_with_incorret_raw_password_raises(
        self, user_in_repo, user_repository, password_hasher
    ) -> None:
        verify_user_credentials: VerifyUserCredentials = VerifyUserCredentials(
            user_repository, password_hasher
        )

        with pytest.raises(InvalidCredentials):
            verify_user_credentials.execute(
                user_name=user_in_repo.user_name, password='senha_errada'
            )
