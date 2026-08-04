import pytest

from user_manager.core.domain.exceptions import InsufficientPrivileges
from user_manager.core.use_cases.update_full_name import UpdateUserFullName


@pytest.fixture
def update_user_full_name(user_repository, regular_user) -> UpdateUserFullName:
    user_repository.save(regular_user)

    update_user_full_name: UpdateUserFullName = UpdateUserFullName(
        user_repository
    )
    return update_user_full_name


class TestUpdateUserFullName:
    def test_admin_can_update_regular_user_full_name(
        self, regular_user, admin_user, user_repository, update_user_full_name
    ) -> None:

        update_user_full_name.execute(
            actor=admin_user, user_id=regular_user.id, new_full_name='new_name'
        )
        assert (
            user_repository.get_by_id(regular_user.id).full_name == 'new_name'
        )

    def test_regular_user_can_update_its_own_full_name(
        self, regular_user, user_repository, update_user_full_name
    ) -> None:

        update_user_full_name.execute(
            actor=regular_user,
            user_id=regular_user.id,
            new_full_name='new_name',
        )
        assert (
            user_repository.get_by_id(regular_user.id).full_name == 'new_name'
        )

    def test_regular_user_cant_update_others_full_name(
        self, regular_user, admin_user, update_user_full_name
    ) -> None:
        with pytest.raises(InsufficientPrivileges):
            update_user_full_name.execute(
                actor=regular_user,
                user_id=admin_user.id,
                new_full_name='new_name',
            )

    def test_cant_update_full_name_passing_wrong_user_id(
        self, regular_user, update_user_full_name
    ) -> None:
        with pytest.raises(InsufficientPrivileges):
            update_user_full_name.execute(
                actor=regular_user,
                user_id=123456789,
                new_full_name='new_name',
            )
