from uuid import uuid4

import pytest

from user_manager.core.domain.exceptions import (
    EmailAlreadyInUse,
    InsufficientPrivileges,
)
from user_manager.core.use_cases.update_user_email import UpdateUserEmail


@pytest.fixture
def update_user_email(user_repository, regular_user) -> UpdateUserEmail:
    user_repository.save(regular_user)

    update_user_email: UpdateUserEmail = UpdateUserEmail(user_repository)
    return update_user_email


class TestUpdateUserEmail:
    def test_admin_can_update_regular_user_email(
            self, regular_user, admin_user, user_repository, update_user_email
    ) -> None:
        update_user_email.execute(
            actor=admin_user, user_id=regular_user.id, new_email='new_name'
        )
        assert user_repository.get_by_id(regular_user.id).email == 'new_name'

    def test_regular_user_can_update_its_own_email(
            self, regular_user, user_repository, update_user_email
    ) -> None:
        update_user_email.execute(
            actor=regular_user,
            user_id=regular_user.id,
            new_email='new_name',
        )
        assert user_repository.get_by_id(regular_user.id).email == 'new_name'

    def test_regular_user_cant_update_others_email(
            self, regular_user, admin_user, update_user_email
    ) -> None:
        with pytest.raises(InsufficientPrivileges):
            update_user_email.execute(
                actor=regular_user,
                user_id=admin_user.id,
                new_email='new_name',
            )

    def test_cant_update_email_passing_wrong_user_id(
            self, regular_user, update_user_email
    ) -> None:
        with pytest.raises(InsufficientPrivileges):
            update_user_email.execute(
                actor=regular_user,
                user_id=uuid4(),
                new_email='new_name',
            )

    def test_cant_use_already_existing_email(
            self, regular_user, admin_user, user_repository, update_user_email
    ) -> None:
        user_repository.save(regular_user)
        user_repository.save(admin_user)
        with pytest.raises(EmailAlreadyInUse):
            update_user_email.execute(
                actor=regular_user,
                user_id=regular_user.id,
                new_email=admin_user.email,
            )
