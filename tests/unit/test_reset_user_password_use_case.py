from uuid import uuid4

import pytest

from user_manager.core.domain.exceptions import (
    InsufficientPrivileges,
    UserNotFound,
)
from user_manager.core.domain.user import User
from user_manager.core.use_cases.reset_user_password import ResetUserPassword


@pytest.fixture
def reset_user_password(
    user_repository, regular_user, password_hasher
) -> ResetUserPassword:
    user_repository.save(regular_user)

    reset_user_password: ResetUserPassword = ResetUserPassword(
        user_repository, password_hasher
    )
    return reset_user_password


class TestResetUserPassword:
    def test_admin_can_reset_users_password(
        self,
        admin_user,
        reset_user_password,
        regular_user,
        user_repository,
        password_hasher,
    ) -> None:
        user_repository.save(regular_user)

        reset_user_password.execute(
            actor=admin_user, user_id=regular_user.id, new_password='nova_senha'
        )

        assert user_repository.get_by_id(
            regular_user.id
        ).password_hash == password_hasher.hash('nova_senha')

    def test_regular_user_cant_reset_its_own_password(
        self,
        regular_user,
        user_repository,
        reset_user_password,
    ) -> None:
        user_repository.save(regular_user)

        with pytest.raises(InsufficientPrivileges):
            reset_user_password.execute(
                actor=regular_user,
                user_id=regular_user.id,
                new_password='nova_senha',
            )

    def test_regular_user_cant_reset_others_password(
        self,
        regular_user,
        reset_user_password,
        valid_user_data,
    ) -> None:

        other_user: User = User.create(
            full_name=valid_user_data['full_name'],
            user_name=valid_user_data['user_name'],
            email=valid_user_data['email'],
            date_of_birth=valid_user_data['date_of_birth'],
            password_hash=valid_user_data['password_hash'],
        )

        with pytest.raises(InsufficientPrivileges):
            reset_user_password.execute(
                actor=regular_user,
                user_id=other_user.id,
                new_password='1234',
            )

    def test_passing_wrong_id_raises(
        self, admin_user, reset_user_password
    ) -> None:

        with pytest.raises(UserNotFound):
            reset_user_password.execute(
                actor=admin_user,
                user_id=uuid4(),
                new_password='1234',
            )
