from typing import Any

from tests.fakes import FakePasswordHasher, FakeUserRepository
from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole
from user_manager.core.use_cases.register_user import RegisterUser


def test_register_create_active_user_with_default_role(valid_user_data) -> None:
    user_repo = FakeUserRepository()
    password_hasher = FakePasswordHasher()
    use_case = RegisterUser(user_repo, password_hasher)

    created: User = use_case.execute(
        full_name=valid_user_data['full_name'],
        user_name=valid_user_data['user_name'],
        email=valid_user_data['email'],
        date_of_birth=valid_user_data['date_of_birth'],
        password='password123',
    )

    assert created.is_active is True
    assert user_repo.memory[created.id] == created
    assert created.password_hash == password_hasher.hash('password123')
    assert created.roles == {UserRole.USER}
