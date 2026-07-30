from datetime import date

import pytest

from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    InsufficientPrivileges,
    UsernameAlreadyInUse,
)
from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole
from user_manager.core.use_cases.create_user import CreateUser

from ..fakes import FakePasswordHasher, FakeUserRepository


class TestCreateUser:
    user_repo = FakeUserRepository()
    password_hasher = FakePasswordHasher()

    def test_create_user_creates_user(
        self, valid_user_data, admin_user
    ) -> None:

        use_case = CreateUser(self.user_repo, self.password_hasher)

        created: User = use_case.execute(
            actor=admin_user,
            full_name=valid_user_data['full_name'],
            user_name=valid_user_data['user_name'],
            email=valid_user_data['email'],
            date_of_birth=valid_user_data['date_of_birth'],
            password='password123',
        )

        assert created.is_active is True
        assert self.user_repo.memory[created.id] == created
        assert created.password_hash == self.password_hasher.hash('password123')
        assert created.roles == {UserRole.USER}

    def test_create_user_with_already_existing_user_name_raises_error(
        self, valid_user_data, admin_user
    ) -> None:
        use_case = CreateUser(self.user_repo, self.password_hasher)

        with pytest.raises(UsernameAlreadyInUse):
            use_case.execute(
                actor=admin_user,
                full_name=valid_user_data['full_name'],
                user_name=valid_user_data['user_name'],
                email='differentmail@mail.com',
                date_of_birth=valid_user_data['date_of_birth'],
                password='password123',
            )

    def test_create_user_with_already_existing_email_raises_error(
        self, valid_user_data, admin_user
    ) -> None:
        use_case = CreateUser(self.user_repo, self.password_hasher)

        with pytest.raises(EmailAlreadyInUse):
            use_case.execute(
                actor=admin_user,
                full_name=valid_user_data['full_name'],
                user_name='differentusername',
                email=valid_user_data['email'],
                date_of_birth=valid_user_data['date_of_birth'],
                password='password123',
            )

    def test_create_user_with_user_actor_raises_error(
        self, regular_user
    ) -> None:
        use_case = CreateUser(self.user_repo, self.password_hasher)

        with pytest.raises(InsufficientPrivileges):
            use_case.execute(
                actor=regular_user,
                full_name='Joao Silva',
                user_name='JoaoSilva',
                email='Joao@email.com',
                date_of_birth=date(1990, 1, 1),
                password='password123',
            )
