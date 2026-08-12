from uuid import uuid4

import pytest

from user_manager.core.domain.exceptions import (
    InsufficientPrivileges,
    InvalidCredentials,
)
from user_manager.core.domain.user import User
from user_manager.core.use_cases.change_user_password import ChangeUserPassword


@pytest.fixture
def change_user_password(
        user_repository, regular_user, password_hasher
) -> ChangeUserPassword:
    user_repository.save(regular_user)

    change_user_password: ChangeUserPassword = ChangeUserPassword(
        user_repository, password_hasher
    )
    return change_user_password


class TestChangeUserPassword:
    def test_regular_user_can_change_its_own_password(
            self,
            regular_user,
            user_repository,
            change_user_password,
            password_hasher,
    ) -> None:
        change_user_password.execute(
            actor=regular_user,
            user_id=regular_user.id,
            current_password='senha_da_silva',
            new_password='1234',
        )
        assert user_repository.get_by_id(
            regular_user.id
        ).password_hash == password_hasher.hash('1234')

    def test_regular_user_cant_change_others_password(
            self,
            regular_user,
            user_repository,
            change_user_password,
            password_hasher,
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
            change_user_password.execute(
                actor=regular_user,
                user_id=other_user.id,
                current_password='senha_da_silva',
                new_password='1234',
            )

    def test_passing_wrong_id_raises(
            self, regular_user, change_user_password
    ) -> None:
        with pytest.raises(InsufficientPrivileges):
            change_user_password.execute(
                actor=regular_user,
                user_id=uuid4(),
                current_password='senha_da_silva',
                new_password='1234',
            )

    def test_cant_change_if_current_password_doesnt_match(
            self,
            regular_user,
            user_repository,
            change_user_password,
    ) -> None:
        user_repository.save(regular_user)

        with pytest.raises(InvalidCredentials):
            change_user_password.execute(
                actor=regular_user,
                user_id=regular_user.id,
                current_password='senha_da_silva_errada',
                new_password='1234',
            )
