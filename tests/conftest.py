from datetime import date, datetime, timezone
from typing import Any

import pytest

from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole
from user_manager.core.ports.secondary.password_hasher import PasswordHasher
from user_manager.core.ports.secondary.user_repository import UserRepository

from .fakes import FakePasswordHasher, FakeUserRepository


@pytest.fixture
def valid_user_data() -> dict[str, Any]:
    return {
        'full_name': 'Test User',
        'user_name': 'fake_user_name',
        'email': 'fakemail@mail.com',
        'date_of_birth': date(2000, 8, 7),
        'password_hash': 'fake_password_hash',
        'is_active': True,
        'created_at': datetime(2026, 7, 24, tzinfo=timezone.utc),
        'updated_at': datetime(2026, 7, 24, tzinfo=timezone.utc),
        'roles': {UserRole.USER},
    }


@pytest.fixture
def admin_user() -> User:
    return User.create(
        full_name='Admin da silva',
        user_name='Adm',
        email='Admin@mail.com',
        date_of_birth=date(2000, 8, 7),
        password_hash='fake_admin_password_hash',
        roles={UserRole.ADMIN},
    )


@pytest.fixture
def regular_user(password_hasher) -> User:
    return User.create(
        full_name='Usuario da Silva',
        user_name='Silva_3000',
        email='silva@mail.com',
        date_of_birth=date(2008, 1, 1),
        password_hash=password_hasher.hash('senha_da_silva'),
    )


@pytest.fixture
def user_repository() -> UserRepository:
    return FakeUserRepository()


@pytest.fixture
def password_hasher() -> PasswordHasher:
    return FakePasswordHasher()
