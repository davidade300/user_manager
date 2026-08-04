import pytest

from user_manager.core.domain.exceptions import InsufficientPrivileges
from user_manager.core.domain.user import User
from user_manager.core.use_cases.create_user import CreateUser
from user_manager.core.use_cases.get_user import GetUser

from ..fakes import FakePasswordHasher, FakeUserRepository


@pytest.fixture
def create_user(
    user_repository: FakeUserRepository, password_hasher: FakePasswordHasher
) -> CreateUser:
    return CreateUser(user_repository, password_hasher)


class TestGetUser:
    def test_admin_can_execute_get_user_for_regular_use(
        self,
        valid_user_data,
        create_user,
        user_repository,
        admin_user,
    ) -> None:
        get_user: GetUser = GetUser(user_repository)
        created: User = create_user.execute(
            actor=admin_user,
            full_name=valid_user_data['full_name'],
            user_name=valid_user_data['user_name'],
            email=valid_user_data['email'],
            date_of_birth=valid_user_data['date_of_birth'],
            password=valid_user_data['password_hash'],
        )

        user: User | None = get_user.execute(
            actor=admin_user, user_id=created.id
        )
        assert user == created

    def test_regular_user_can_get_itself(
        self, regular_user, user_repository
    ) -> None:
        get_user: GetUser = GetUser(user_repository)
        user_repository.save(regular_user)
        user: User | None = get_user.execute(
            actor=regular_user, user_id=regular_user.id
        )

        assert user == regular_user

    def test_regular_user_cannot_get_other_user(
        self,
        regular_user,
        user_repository,
        create_user,
        admin_user,
        valid_user_data,
    ) -> None:
        get_user: GetUser = GetUser(user_repository)
        user_repository.save(regular_user)
        other_user: User = create_user.execute(
            actor=admin_user,
            full_name=valid_user_data['full_name'],
            user_name=valid_user_data['user_name'],
            email=valid_user_data['email'],
            date_of_birth=valid_user_data['date_of_birth'],
            password=valid_user_data['password_hash'],
        )
        with pytest.raises(InsufficientPrivileges):
            get_user.execute(actor=regular_user, user_id=other_user.id)
