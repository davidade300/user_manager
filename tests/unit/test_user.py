from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
import time_machine

from user_manager.core.domain.exceptions import (
    DeactivatedUser,
    RoleAlreadyAssigned,
    RoleNotAssigned,
    UserMustHaveAtLeastOneRole,
)
from user_manager.core.domain.user import User
from user_manager.core.domain.user_role import UserRole


def make_user(
    user_data: dict[str, Any], roles: set[UserRole] | None = None
) -> User:
    user: User = User.create(
        full_name=user_data['full_name'],
        user_name=user_data['user_name'],
        email=user_data['email'],
        date_of_birth=user_data['date_of_birth'],
        password_hash=user_data['password_hash'],
        roles=roles,
    )
    return user


def test_create_returns_active_user_with_default_role(valid_user_data) -> None:
    user: User = make_user(valid_user_data)

    assert user.is_active is True
    assert user.roles == {UserRole.USER}


def test_create_returns_user_with_given_roles(valid_user_data) -> None:
    user: User = make_user(
        valid_user_data, roles={UserRole.ADMIN, UserRole.USER}
    )
    assert user.roles == {UserRole.USER, UserRole.ADMIN}


def test_changing_roles_property_doesnt_affect_user_roles(
    valid_user_data,
) -> None:
    user: User = make_user(valid_user_data)

    with pytest.raises(AttributeError):
        user.roles.add(UserRole.ADMIN)  # type: ignore

    assert user.roles == {UserRole.USER}


def test_init_with_empty_roles_raises_error(valid_user_data) -> None:
    user_data = {**valid_user_data, 'roles': set(), 'id': uuid4()}

    with pytest.raises(UserMustHaveAtLeastOneRole):
        # pyrefly: ignore [bad-argument-type]
        User(**user_data)


def test_revoking_last_role_raises_error(valid_user_data) -> None:
    user: User = make_user(valid_user_data)

    with pytest.raises(UserMustHaveAtLeastOneRole):
        user.revoke_role(UserRole.USER)

    assert user.roles == {UserRole.USER}


def test_revoking_inexistent_role_raises_error(valid_user_data) -> None:
    user: User = make_user(valid_user_data)

    with pytest.raises(RoleNotAssigned):
        user.revoke_role(UserRole.ADMIN)

    assert UserRole.ADMIN not in user.roles


def test_granting_existing_role_raises_error(valid_user_data) -> None:
    user: User = make_user(valid_user_data)

    with pytest.raises(RoleAlreadyAssigned):
        user.grant_role(UserRole.USER)

    assert user.roles == {UserRole.USER}


def test_granting_new_role_adds_it(valid_user_data) -> None:
    user: User = make_user(valid_user_data)
    user.grant_role(UserRole.ADMIN)

    assert user.roles == {UserRole.USER, UserRole.ADMIN}


def test_granting_role_to_deactivated_user_raises_error(
    valid_user_data,
) -> None:
    user: User = make_user(valid_user_data)
    user.deactivate()
    with pytest.raises(DeactivatedUser):
        user.grant_role(UserRole.ADMIN)


def test_user_repr_doesnt_contain_password_hash(valid_user_data) -> None:
    user: User = make_user(valid_user_data)

    assert 'password_hash' not in repr(user)


def test_hash_returns_current_user_id(valid_user_data) -> None:
    user: User = make_user(valid_user_data)

    assert hash(user) == hash(user.id)


@pytest.mark.parametrize(
    'actions',
    [
        lambda u: u.update_full_name('new name'),
        lambda u: u.update_email('new_email'),
    ],
)
def test_updating_inactive_user_data_raises_error(
    actions, valid_user_data
) -> None:
    user: User = make_user(valid_user_data)
    user.deactivate()

    with pytest.raises(DeactivatedUser):
        actions(user)


def test_password_can_be_changed_on_deactivated_user(valid_user_data) -> None:
    user: User = make_user(valid_user_data)
    user.deactivate()
    user.update_password_hash('new_password_hash')

    assert user.password_hash == 'new_password_hash'


def test__touch_updates_updated_at(valid_user_data) -> None:
    user: User = make_user(valid_user_data)
    traveller = time_machine.travel(
        datetime(2026, 7, 25, tzinfo=timezone.utc), tick=False
    )
    with traveller:
        user.grant_role(UserRole.ADMIN)

    assert user.updated_at.timestamp() == traveller.destination_timestamp


def test_revoke_role_works_on_deactivated_user(valid_user_data) -> None:
    user: User = make_user(valid_user_data)
    user.grant_role(UserRole.ADMIN)
    user.deactivate()
    user.revoke_role(UserRole.ADMIN)

    assert user.roles == {UserRole.USER}


def test_users_with_same_id_are_equal(valid_user_data) -> None:
    user_id: UUID = uuid4()
    # pyrefly: ignore [bad-argument-type]
    user: User = User(**{**valid_user_data, 'id': user_id})
    same_id_user: User = User(
        # pyrefly: ignore [bad-argument-type]
        **{**valid_user_data, 'full_name': 'Other Name', 'id': user_id}
    )

    assert user == same_id_user


def test_users_with_different_id_are_not_equal(valid_user_data) -> None:
    # pyrefly: ignore [bad-argument-type]
    user: User = User(**{**valid_user_data, 'id': uuid4()})
    # pyrefly: ignore [bad-argument-type]
    other_user: User = User(**{**valid_user_data, 'id': uuid4()})

    assert user != other_user


def test_is_admin_true_when_user_has_admin_role(valid_user_data) -> None:
    user: User = make_user(valid_user_data, roles={UserRole.ADMIN})

    assert user.is_admin() is True


def test_is_admin_false_when_user_lacks_admin_role(valid_user_data) -> None:
    user: User = make_user(valid_user_data)

    assert user.is_admin() is False
