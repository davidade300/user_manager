import pytest

from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    UsernameAlreadyInUse,
)
from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole
from user_manager.core.use_cases.register_user import RegisterUser

from ..fakes import FakePasswordHasher, FakeUserRepository


def test_register_create_active_user_with_default_role(valid_user_data) -> None:
    user_repo = FakeUserRepository()
    password_hasher = FakePasswordHasher()
    use_case = RegisterUser(user_repo, password_hasher)

    registered: User = use_case.execute(
        full_name=valid_user_data['full_name'],
        user_name=valid_user_data['user_name'],
        email=valid_user_data['email'],
        date_of_birth=valid_user_data['date_of_birth'],
        password='password123',
    )

    assert registered.is_active is True
    assert user_repo.memory[registered.id] == registered
    assert registered.password_hash == password_hasher.hash('password123')
    assert registered.roles == {UserRole.USER}


def test_register_user_with_already_existing_user_name_raises_error(
    valid_user_data,
) -> None:
    user_repo = FakeUserRepository()
    password_hasher = FakePasswordHasher()
    use_case = RegisterUser(user_repo, password_hasher)

    use_case.execute(
        full_name=valid_user_data['full_name'],
        user_name=valid_user_data['user_name'],
        email=valid_user_data['email'],
        date_of_birth=valid_user_data['date_of_birth'],
        password='password123',
    )

    with pytest.raises(UsernameAlreadyInUse):
        use_case.execute(
            full_name=valid_user_data['full_name'],
            user_name=valid_user_data['user_name'],
            email='different_email',
            date_of_birth=valid_user_data['date_of_birth'],
            password='password123',
        )


def test_register_user_with_already_existing_email_raises_error(
    valid_user_data,
) -> None:
    user_repo = FakeUserRepository()
    password_hasher = FakePasswordHasher()
    use_case = RegisterUser(user_repo, password_hasher)

    use_case.execute(
        full_name=valid_user_data['full_name'],
        user_name=valid_user_data['user_name'],
        email=valid_user_data['email'],
        date_of_birth=valid_user_data['date_of_birth'],
        password='password123',
    )

    with pytest.raises(EmailAlreadyInUse):
        use_case.execute(
            full_name=valid_user_data['full_name'],
            user_name='different_username',
            email=valid_user_data['email'],
            date_of_birth=valid_user_data['date_of_birth'],
            password='password123',
        )
